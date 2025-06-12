import sqlite3
import pandas as pd
import numpy as np
import faiss
import pickle
import os
import logging
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

logger = logging.getLogger(__name__)

class MedicalEntityLinker:
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MedicalEntityLinker, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # Configuración de paths
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        self.MODEL_NAME = "pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb"
        self.FAISS_INDEX_PATH = os.path.join(self.BASE_DIR, "data/OMOP_SNOMED/faiss_snomed.index")
        self.ID_MAPPING_PATH = os.path.join(self.BASE_DIR, "data/OMOP_SNOMED/concept_ids.pkl")
        self.SYNONYMS_PATH = os.path.join(self.BASE_DIR, "data/OMOP_SNOMED/synonyms.parquet")
        self.DB_PATH = os.path.join(self.BASE_DIR, "data/OMOP_SNOMED/omop_snomed.db")

        self.embedding_cache = {}
        
        # Variables para lazy loading
        self.model = None
        self.index = None
        self.concept_ids = None
        self.syn_df = None
        
        self._initialized = True
        logger.info("MedicalEntityLinker initialized (lazy loading mode)")
    
    def _ensure_model_loaded(self):
        """Lazy loading del modelo SentenceTransformer"""
        if self.model is None:
            try:
                logger.info("Loading SentenceTransformer model...")
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.MODEL_NAME)
                logger.info("SentenceTransformer model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading SentenceTransformer model: {e}")
                raise
                
    def _ensure_index_loaded(self):
        """Lazy loading del índice FAISS y datos relacionados"""
        if self.index is None:
            try:
                logger.info("Loading FAISS indexes and data...")
                self._load_vector_index()
                self._test_db_connection()
                logger.info("FAISS indexes and data loaded successfully")
            except Exception as e:
                logger.error(f"Error loading FAISS indexes: {e}")
                raise
    
    def _load_vector_index(self):
        """Cargar índice FAISS y datos relacionados"""
        # Verificar que los archivos existen
        if not os.path.exists(self.FAISS_INDEX_PATH):
            raise FileNotFoundError(f"FAISS index not found: {self.FAISS_INDEX_PATH}")
        if not os.path.exists(self.ID_MAPPING_PATH):
            raise FileNotFoundError(f"ID mapping not found: {self.ID_MAPPING_PATH}")
        if not os.path.exists(self.SYNONYMS_PATH):
            raise FileNotFoundError(f"Synonyms file not found: {self.SYNONYMS_PATH}")
            
        # Cargar índice FAISS
        self.index = faiss.read_index(self.FAISS_INDEX_PATH)
        
        # Cargar mapeo de IDs
        with open(self.ID_MAPPING_PATH, "rb") as f:
            self.concept_ids = pickle.load(f)
        
        # Cargar sinónimos
        self.syn_df = pd.read_parquet(self.SYNONYMS_PATH)
        
        logger.info(f"Loaded {self.index.ntotal} vectors and {len(self.syn_df)} synonyms")
    
    def _test_db_connection(self):
        """Verificar conexión a la base de datos"""
        if not os.path.exists(self.DB_PATH):
            raise FileNotFoundError(f"OMOP database not found: {self.DB_PATH}")
            
        with sqlite3.connect(self.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM concepts LIMIT 1")
            count = cursor.fetchone()[0]
            logger.info(f"OMOP database contains {count:,} concepts")
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Obtener embedding con cache"""
        if text not in self.embedding_cache:
            self._ensure_model_loaded()
            self.embedding_cache[text] = self.model.encode([text]).astype("float32")
        return self.embedding_cache[text]
    
    def search_synonym(self, text: str, k: int = 10) -> List[Tuple[int, str, float]]:
        """Buscar sinónimos similares"""
        self._ensure_index_loaded()
        
        query_vec = self._get_embedding(text)
        
        distances, indices = self.index.search(query_vec, k)
        
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx != -1:
                concept_id = self.concept_ids[idx]
                synonym = self.syn_df.iloc[idx]["concept_synonym_name"]
                results.append((concept_id, synonym, float(distance)))
        
        return results
    
    def get_omop_concepts_batch(self, concept_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """Obtener conceptos OMOP en lote"""
        if not concept_ids:
            return {}
        
        with sqlite3.connect(self.DB_PATH) as conn:
            placeholders = ','.join('?' * len(concept_ids))
            query = f"""
            SELECT concept_id, concept_name, domain_id, vocabulary_id, 
                   concept_class_id, standard_concept, concept_code, invalid_reason
            FROM concepts 
            WHERE concept_id IN ({placeholders})
            """
            
            df = pd.read_sql_query(query, conn, params=concept_ids)
            return df.set_index('concept_id').to_dict('index')
    
    def get_similar_terms_optimized(self, term: str, k: int = 50) -> List[Dict[str, Any]]:
        """Buscar términos similares optimizado"""
        logger.info(f"Searching similar terms for: '{term}'")
        
        try:
            # Buscar sinónimos similares
            similar_results = self.search_synonym(term, k=k)
            
            if not similar_results:
                logger.warning(f"No results found for: '{term}'")
                return []
            
            # Obtener conceptos OMOP
            concept_ids = [result[0] for result in similar_results]
            omop_concepts = self.get_omop_concepts_batch(concept_ids)
            
            results = []
            for concept_id, synonym, distance in similar_results:
                concept_info = omop_concepts.get(concept_id, {})
                
                # Filtrar conceptos inválidos
                if concept_info.get('invalid_reason') is not None:
                    continue
                
                # Convertir distancia a similarity score
                similarity_score = max(0.0, 1.0 / (1.0 + distance))
                
                results.append({
                    "term": str(synonym),
                    "preferred_term": str(concept_info.get('concept_name', '')),
                    "concept_id": int(concept_id),
                    "semantic_tag": str(concept_info.get('domain_id', '')),
                    "similarity": round(similarity_score, 4),
                    "vocabulary": str(concept_info.get('vocabulary_id', '')),
                    "concept_class": str(concept_info.get('concept_class_id', ''))
                })
            
            logger.info(f"Found {len(results)} valid terms for '{term}'")
            return results
            
        except Exception as e:
            logger.error(f"Error in get_similar_terms_optimized: {e}")
            return []
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del cache"""
        cache_size_mb = sum(arr.nbytes for arr in self.embedding_cache.values()) / (1024*1024)
        return {
            'cached_terms': len(self.embedding_cache),
            'cache_size_mb': round(cache_size_mb, 2),
            'total_vectors': self.index.ntotal if self.index is not None else 0,
            'model_loaded': self.model is not None,
            'index_loaded': self.index is not None
        }
    
    def clear_cache(self):
        """Limpiar cache de embeddings"""
        old_size = len(self.embedding_cache)
        self.embedding_cache.clear()
        logger.info(f"Cache cleared: {old_size} terms removed")


# Variables globales para singleton
_entity_linker = None

def get_entity_linker() -> MedicalEntityLinker:
    """Obtener instancia del entity linker (singleton con lazy loading)"""
    global _entity_linker
    if _entity_linker is None:
        _entity_linker = MedicalEntityLinker()
    return _entity_linker

def get_similar_terms_bd(term: str, k: int = 50) -> List[Dict[str, Any]]:
    """Buscar términos similares en la base de datos OMOP"""
    try:
        linker = get_entity_linker()
        return linker.get_similar_terms_optimized(term, k=k)
    except Exception as e:
        logger.error(f"Error in get_similar_terms_bd: {e}")
        return []

def get_similarity_stats() -> Dict[str, Any]:
    """Obtener estadísticas del servicio de similaridad"""
    try:
        linker = get_entity_linker()
        return linker.get_cache_stats()
    except Exception as e:
        logger.error(f"Error obtaining statistics: {e}")
        return {"error": str(e)}