# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importa tus servicios médicos reorganizados
from app.medical.ner import extract_medical_terms
from app.medical.ner_es import extract_medical_terms_es
from app.medical.similarity import get_similar_terms
from app.medical.similarity_bd import get_similar_terms_bd
from app.medical.models import (
    TextInput, TextEntities, Entity,
    SimilarTermInput, SimilarTerm, SimilarTermList
)

# Importa routers y base de datos de auth reorganizados
from app.auth.routes import router as auth_router
from app.query_routes import router as query_router
from app.auth.database import Base as AuthBase, engine as auth_engine

# NUEVO: Importar router de generación SQL
from app.sql_generation.routes import router as sql_generation_router

from dotenv import load_dotenv
load_dotenv() 

app = FastAPI(
    title="Cortex Medical API",
    description="API para análisis médico con NER, búsqueda de términos y generación SQL",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crea las tablas de autenticación (usuarios y logs) al arrancar
AuthBase.metadata.create_all(bind=auth_engine)

logger.info("🔥 Iniciando Cortex Medical API")

# --- Routers ---
app.include_router(auth_router)              # /auth/register, /auth/login
app.include_router(query_router)             # /queries/  (protegido por JWT)
app.include_router(sql_generation_router)    # /sql-generation/ (protegido por JWT)

# --- Endpoints originales ---

@app.post("/extract", response_model=TextEntities)
def extract_entities(input: TextInput):
    """Extraer entidades médicas de texto en inglés"""
    entities_raw = extract_medical_terms(input.text)
    entities = [Entity(**e) for e in entities_raw]
    return TextEntities(entities=entities)

@app.post("/extractEs", response_model=TextEntities)
def extract_entities_es(input: TextInput):
    """Extraer entidades médicas de texto en español"""
    entities_raw = extract_medical_terms_es(input.text)
    entities = [Entity(**e) for e in entities_raw]
    return TextEntities(entities=entities)

@app.post("/similar", response_model=SimilarTermList)
def similar_terms(input: SimilarTermInput):
    """Buscar términos médicos similares usando API SNOMED"""
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
    """Buscar términos médicos similares usando base de datos local"""
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

@app.get("/")
def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "Cortex Medical API",
        "version": "1.0.0",
        "endpoints": {
            "auth": "/auth/",
            "medical_ner": "/extract, /extractEs",
            "similarity": "/similar, /test", 
            "sql_generation": "/sql-generation/",
            "health": "/sql-generation/health"
        }
    }