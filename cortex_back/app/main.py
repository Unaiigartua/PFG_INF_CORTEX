# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importa tus routers originales
from app.ner import extract_medical_terms
from app.similarity import get_similar_terms
from app.similarity_bd import get_similar_terms_bd
from app.models import (
    TextInput, TextEntities, Entity,
    SimilarTermInput, SimilarTerm, SimilarTermList
)

# Importa routers y base de datos de auth
from app.auth_routes import router as auth_router
from app.query_routes import router as query_router
from app.auth_database import Base as AuthBase, engine as auth_engine

from dotenv import load_dotenv
load_dotenv() 


app = FastAPI(title="Mi API con Auth + Logs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crea las tablas de autenticación (usuarios y logs) al arrancar
AuthBase.metadata.create_all(bind=auth_engine)

# Si usas create_all para tus tablas principales, descomenta estas líneas:
# MainBase.metadata.create_all(bind=main_engine)

print("🔥 Se está ejecutando main.py")

# --- Routers de Auth y Logs ---
app.include_router(auth_router)    # /auth/register, /auth/login
app.include_router(query_router)   # /queries/  (protegido por JWT)

# --- Endpoints originales ---

@app.post("/extract", response_model=TextEntities)
def extract_entities(input: TextInput):
    entities_raw = extract_medical_terms(input.text)
    entities = [Entity(**e) for e in entities_raw]
    return TextEntities(entities=entities)

@app.post("/similar", response_model=SimilarTermList)
def similar_terms(input: SimilarTermInput):
    raw_results = get_similar_terms(input.term)
    results = [
        SimilarTerm(
            term=item["term"],
            preferred_term=item["preferred_term"],
            concept_id=item["concept_id"],
            similarity=item["similarity"],
            semantic_tag=item["semantic_tag"]
        )
        for item in raw_results
    ]
    return SimilarTermList(results=results)

@app.post("/test", response_model=SimilarTermList)
def similar_terms_db(input: SimilarTermInput):
    raw_results = get_similar_terms_bd(input.term)
    results = [
        SimilarTerm(
            term=str(item["term"]),
            preferred_term=str(item["preferred_term"]),
            concept_id=str(item["concept_id"]),
            similarity=float(item["similarity"]),
            semantic_tag=str(item["semantic_tag"])
        )
        for item in raw_results
    ]
    return SimilarTermList(results=results)
