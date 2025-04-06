import sqlite3
import pandas as pd
import numpy as np
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from typing import List, Tuple
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_PATH = os.path.join(BASE_DIR, "OMOP_SNOMED/CONCEPT_SYNONYM.csv")
MODEL_NAME = "pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb"

FAISS_INDEX_PATH = os.path.join(BASE_DIR, "OMOP_SNOMED/faiss_snomed.index")
ID_MAPPING_PATH = os.path.join(BASE_DIR, "OMOP_SNOMED/concept_ids.pkl")
SYNONYMS_PATH = os.path.join(BASE_DIR, "OMOP_SNOMED/synonyms.parquet")

model = SentenceTransformer(MODEL_NAME)


def find_concept_by_code(code: str, conn):
    query = """
    SELECT concept_id, concept_name, domain_id, vocabulary_id, standard_concept
    FROM concepts
    WHERE concept_code = ?
    """
    return pd.read_sql_query(query, conn, params=(code,))






# print(find_concept_by_code("392021009", conn))


def load_vector_index():
    index = faiss.read_index(FAISS_INDEX_PATH)
    with open(ID_MAPPING_PATH, "rb") as f:
        concept_ids = pickle.load(f)
    syn_df = pd.read_parquet(SYNONYMS_PATH)
    return index, concept_ids, syn_df


def search_synonym(text: str, k: int = 10) -> List[Tuple[int, str]]:
    query_vec = model.encode([text]).astype("float32")

    index, concept_ids, syn_df = load_vector_index()
    distances, indices = index.search(query_vec, k)

    results = []
    for idx in indices[0]:
        cid = concept_ids[idx]
        synonym = syn_df.iloc[idx]["concept_synonym_name"]
        results.append((cid, synonym))

    return results


def find_concept_by_code_OMOP(code: str, conn):
    query = """
    SELECT concept_id, concept_name, domain_id, vocabulary_id, standard_concept, invalid_reason
    FROM concepts
    WHERE concept_id = ?
    """
    return pd.read_sql_query(query, conn, params=(code,))

def get_similar_terms_bd(term):

    conn = sqlite3.connect(os.path.join(BASE_DIR, "OMOP_SNOMED/omop_snomed.db"))

    similar_results = search_synonym(term, k=50)
    # for cid, name in results:
    #     print(f" - {cid} → {name}")

    results = []

    for cid, name in similar_results:
        concept_info = find_concept_by_code_OMOP(cid, conn)
        # print(f"Concept ID: {cid}, Concept Name: {name}, Preferred Name: {concept_info['concept_name'].values[0]}, Domain: {concept_info['domain_id'].values[0]}")
        
        if concept_info['invalid_reason'].values[0] != None:
            print (f"Concept ID: {cid} is invalid due to reason: {concept_info['invalid_reason'].values[0]}")
            continue

        results.append({
            "term": name,
            "preferred_term": concept_info['concept_name'].values[0],
            "concept_id": cid,
            "semantic_tag": concept_info['domain_id'].values[0],
            "similarity": 0.0, 
        })


    return results