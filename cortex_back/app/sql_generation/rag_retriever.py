from __future__ import annotations

import pickle
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import logging

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from app.core.config import DATASET_PATH

logger = logging.getLogger(__name__)

# Configuración por defecto
EMBED_MODEL_NAME = "pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb"
K_NEIGHBOURS = 5

class MedicalSQLRetriever:
    """Retriever para buscar ejemplos similares de SQL usando embeddings semánticos"""

    def __init__(self, model_name: str = EMBED_MODEL_NAME):
        self.model = SentenceTransformer(model_name)
        self.index: faiss.Index | None = None
        self.metadata: List[dict] | None = None  # one dict per vector
        self.artifact_dir = Path("rag_index")
        self.index_file = self.artifact_dir / "faiss.index"
        self.meta_file = self.artifact_dir / "metadata.pkl"

    def build(self, dataset_path: Path, question_cols: list[str] | None = None) -> None:
        """Construir el índice RAG desde el dataset"""
        logger.info(f"Loading dataset from {dataset_path}")
        df = pd.read_excel(dataset_path)

        if question_cols is None:
            question_cols = [c for c in df.columns if c.upper().startswith("QUESTION")]
            if not question_cols:
                raise ValueError("No QUESTION* columns found; pass question_cols parameter.")
        else:
            missing = [c for c in question_cols if c not in df.columns]
            if missing:
                raise ValueError(f"Columns not found: {missing}")

        sql_col_candidates = [c for c in df.columns if "QUERY" in c.upper() and "RUNNABLE" in c.upper()]
        if not sql_col_candidates:
            raise ValueError("Couldn't spot a *_RUNNABLE SQL column.")
        sql_col = sql_col_candidates[0]

        questions, metadatas = [], []
        for _, row in df.iterrows():
            variants = [str(row[c]) for c in question_cols if pd.notna(row[c])]
            for variant in variants:
                questions.append(variant)
                metadatas.append(
                    {
                        "row_id": int(row["ID"]) if "ID" in row else None,
                        "canonical_question": str(row[question_cols[0]]),
                        "sql": str(row[sql_col]),
                    }
                )

        logger.info(f"Total question variants: {len(questions):,}")
        logger.info("Computing embeddings...")
        embeds = self.model.encode(questions, show_progress_bar=True, convert_to_numpy=True)
        dim = embeds.shape[1]
        faiss.normalize_L2(embeds)

        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeds)
        self.metadata = metadatas

        # Guardar índice
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_file))
        with self.meta_file.open("wb") as fp:
            pickle.dump(self.metadata, fp)
        logger.info(f"Index built – vectors: {self.index.ntotal}")

    def load(self) -> None:
        """Cargar índice pre-construido"""
        if not self.index_file.exists():
            raise FileNotFoundError(f"Index not found at {self.index_file}; run build() first.")
        
        logger.info(f"Loading RAG index from {self.index_file}")
        self.index = faiss.read_index(str(self.index_file))
        with self.meta_file.open("rb") as fp:
            self.metadata = pickle.load(fp)
        logger.info(f"Index loaded – vectors: {self.index.ntotal}")

    def query(self, text: str, k: int = K_NEIGHBOURS) -> List[Tuple[float, dict]]:
        """Buscar ejemplos similares"""
        if self.index is None or self.metadata is None:
            # Intentar cargar automáticamente
            try:
                self.load()
            except FileNotFoundError:
                logger.error("RAG index not found. Build it first with build() method.")
                return []

        q_emb = self.model.encode([text], convert_to_numpy=True)
        faiss.normalize_L2(q_emb)
        scores, idxs = self.index.search(q_emb, k)
        results = []
        for score, idx in zip(scores[0], idxs[0]):
            if idx == -1:
                continue
            results.append((float(score), self.metadata[idx]))
        return results


class RAGRetriever:
    """Wrapper más simple para usar en el servicio de generación SQL"""
    
    def __init__(self, dataset_path: str = DATASET_PATH):
        self.dataset_path = Path(dataset_path)
        self.retriever: Optional[MedicalSQLRetriever] = None
        self._index_built = False
        
    def _ensure_index_built(self):
        """Asegurar que el índice RAG esté construido"""
        if not self._index_built:
            self._build_index()
            
    def _build_index(self):
        """Construir el índice RAG con todo el dataset"""
        try:
            if not self.dataset_path.exists():
                raise FileNotFoundError(f"Dataset no encontrado: {self.dataset_path}")
            
            logger.info(f"Construyendo índice RAG desde {self.dataset_path}")
            self.retriever = MedicalSQLRetriever()
            
            # Intentar cargar primero, si no existe, construir
            try:
                self.retriever.load()
                logger.info("Índice RAG cargado desde disco")
            except FileNotFoundError:
                logger.info("Construyendo nuevo índice RAG...")
                self.retriever.build(self.dataset_path)
            
            self._index_built = True
            logger.info("Índice RAG listo")
            
        except Exception as e:
            logger.error(f"Error con índice RAG: {e}")
            raise
    
    def get_similar_examples(self, question: str, k: int = 1) -> List[Dict]:
        """Obtener ejemplos similares del RAG"""
        self._ensure_index_built()
        
        if not self.retriever:
            return []
            
        try:
            results = self.retriever.query(question, k=k)
            
            similar_examples = []
            for score, metadata in results:
                similar_examples.append({
                    'question': metadata['canonical_question'],
                    'sql': metadata['sql'],
                    'score': float(score),
                    'row_id': metadata.get('row_id')
                })
            
            return similar_examples
            
        except Exception as e:
            logger.error(f"Error recuperando ejemplos similares: {e}")
            return []
    
    def format_similar_example(self, example: Dict) -> str:
        """Formatear un ejemplo similar para incluir en el prompt"""
        if not example:
            return "No similar examples found."
        
        return f"""Question: {example['question']}
SQL: {example['sql']}"""