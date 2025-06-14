# app/main.py

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.medical.ner import extract_medical_terms
from app.medical.ner_es import extract_medical_terms_es
from app.medical.similarity import get_similar_terms
from app.medical.similarity_bd import get_similar_terms_bd, get_entity_linker, get_similarity_stats
from app.medical.models import (
    TextInput, TextEntities, Entity,
    SimilarTermInput, SimilarTerm, SimilarTermList
)
from app.auth.routes import router as auth_router
from app.query_routes import router as query_router
from app.auth.database import Base as AuthBase, engine as auth_engine
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

AuthBase.metadata.create_all(bind=auth_engine)

def initialize_medical_services():
    try:
        logger.info("Initializing medical services")
        linker = get_entity_linker()
        stats = linker.get_cache_stats()
        logger.info(f"Medical services initialized: {stats}")
    except Exception as e:
        logger.error(f"Error initializing medical services: {e}")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Cortex Medical API")
    
    import threading
    init_thread = threading.Thread(target=initialize_medical_services)
    init_thread.start()

app.include_router(auth_router)
app.include_router(query_router)
app.include_router(sql_generation_router)

@app.post("/extract", response_model=TextEntities)
def extract_entities(input: TextInput):
    entities_raw = extract_medical_terms(input.text)
    entities = [Entity(**e) for e in entities_raw]
    return TextEntities(entities=entities)

@app.post("/extractEs", response_model=TextEntities)
def extract_entities_es(input: TextInput):
    entities_raw = extract_medical_terms_es(input.text)
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

@app.post("/similar_db", response_model=SimilarTermList)
def similar_terms_db(input: SimilarTermInput):
    try:
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
    except Exception as e:
        logger.error(f"Error in similar_terms_db: {e}")
        return SimilarTermList(results=[])

@app.get("/similarity/health")
def similarity_health():
    try:
        stats = get_similarity_stats()
        return {
            "status": "healthy",
            "service": "medical_similarity",
            "stats": stats
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "medical_similarity",
            "error": str(e)
        }

@app.get("/similarity/stats")
def similarity_statistics():
    return get_similarity_stats()

@app.post("/similarity/clear-cache")
def clear_similarity_cache():
    try:
        linker = get_entity_linker()
        old_stats = linker.get_cache_stats()
        linker.clear_cache()
        new_stats = linker.get_cache_stats()
        
        return {
            "status": "success",
            "message": "Cache cleared",
            "before": old_stats,
            "after": new_stats
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/")
def root():
    return {
        "message": "Cortex Medical API",
        "version": "1.0.0",
        "status": "ready",
        "endpoints": {
            "auth": "/auth/",
            "medical_ner": "/extract, /extractEs",
            "similarity": "/similar, /similar_db", 
            "similarity_health": "/similarity/health",
            "similarity_stats": "/similarity/stats",
            "sql_generation": "/sql-generation/",
            "queries": "/queries/",
            "health": "/sql-generation/health"
        }
    }