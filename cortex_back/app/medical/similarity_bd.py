import sqlite3
import pandas as pd
import numpy as np
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Optional, Dict, Any
import os
import logging
from pathlib import Path

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
            
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        self.MODEL_NAME = "pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb"
        self.FAISS_INDEX_PATH = os.path.join(self.BASE_DIR, "app/OMOP_SNOMED/faiss_snomed.index")
        self.ID_MAPPING_PATH = os.path.join(self.BASE_DIR, "app/OMOP_SNOMED/concept_ids.pkl")
        self.SYNONYMS_PATH = os.path.join(self.BASE_DIR, "app/OMOP_SNOMED/synonyms.parquet")
        self.DB_PATH = os.path.join(self.BASE_DIR, "app/OMOP_SNOMED/omop_snomed.db")

        self.embedding_cache = {}
        
        try:
            logger.info("Initializing MedicalEntityLinker")
            
            logger.info("Loading SentenceTransformer model")
            self.model = SentenceTransformer(self.MODEL_NAME)
            
            logger.info("Loading FAISS indexes")
            self._load_vector_index()
            
            logger.info("Verifying database connection")
            self._test_db_connection()
            
            self._initialized = True
            logger.info("MedicalEntityLinker initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing MedicalEntityLinker: {e}")
            raise
    
    def _load_vector_index(self):
        self.index = faiss.read_index(self.FAISS_INDEX_PATH)
        
        with open(self.ID_MAPPING_PATH, "rb") as f:
            self.concept_ids = pickle.load(f)
        
        self.syn_df = pd.read_parquet(self.SYNONYMS_PATH)
        
        logger.info(f"Loaded {self.index.ntotal} vectors and {len(self.syn_df)} synonyms")
    
    def _test_db_connection(self):
        with sqlite3.connect(self.DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM concepts LIMIT 1")
            count = cursor.fetchone()[0]
            logger.info(f"OMOP database contains {count:,} concepts")
    
    def _get_embedding(self, text: str) -> np.ndarray:
        if text not in self.embedding_cache:
            self.embedding_cache[text] = self.model.encode([text]).astype("float32")
        return self.embedding_cache[text]
    
    def search_synonym(self, text: str, k: int = 10) -> List[Tuple[int, str, float]]:
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
        logger.info(f"Searching similar terms for: '{term}'")
        
        similar_results = self.search_synonym(term, k=k)
        
        if not similar_results:
            logger.warning(f"No results found for: '{term}'")
            return []
        
        concept_ids = [result[0] for result in similar_results]
        omop_concepts = self.get_omop_concepts_batch(concept_ids)
        
        results = []
        for concept_id, synonym, distance in similar_results:
            concept_info = omop_concepts.get(concept_id, {})
            
            if concept_info.get('invalid_reason') is not None:
                continue
            
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
    
    def get_cache_stats(self) -> Dict[str, Any]:
        cache_size_mb = sum(arr.nbytes for arr in self.embedding_cache.values()) / (1024*1024)
        return {
            'cached_terms': len(self.embedding_cache),
            'cache_size_mb': round(cache_size_mb, 2),
            'total_vectors': self.index.ntotal if hasattr(self, 'index') else 0
        }
    
    def clear_cache(self):
        old_size = len(self.embedding_cache)
        self.embedding_cache.clear()
        logger.info(f"Cache cleared: {old_size} terms removed")


_entity_linker = None

def get_entity_linker() -> MedicalEntityLinker:
    global _entity_linker
    if _entity_linker is None:
        _entity_linker = MedicalEntityLinker()
    return _entity_linker

def get_similar_terms_bd(term: str, k: int = 50) -> List[Dict[str, Any]]:
    linker = get_entity_linker()
    return linker.get_similar_terms_optimized(term, k=k)

def get_similarity_stats() -> Dict[str, Any]:
    try:
        linker = get_entity_linker()
        return linker.get_cache_stats()
    except Exception as e:
        logger.error(f"Error obtaining statistics: {e}")
        return {"error": str(e)}