from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import your modules (pero los modelos se cargan lazy)
from app.medical.ner import extract_medical_terms
from app.medical.ner_es import extract_medical_terms_es
from app.medical.similarity_bd import (
    get_similar_terms_bd, 
    get_entity_linker, 
    get_similarity_stats
)
from app.medical.models import (
    TextInput, 
    TextEntities, 
    Entity,
    SimilarTermInput, 
    SimilarTerm, 
    SimilarTermList
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Cortex Medical API",
    description="Public API for medical NER and entity linking - no authentication required",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

def validate_text_input(text: str, max_length: int = 10000) -> bool:
    """Validate text input for medical processing"""
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    if len(text) > max_length:
        raise ValueError(f"Text too long. Maximum length: {max_length}")
    
    return True

# NO inicializar modelos en startup - lazy loading
@app.on_event("startup")
async def startup_event():
    logger.info("Cortex Medical API started - models will load on first request")

@app.get("/")
def root():
    return {
        "message": "Cortex Medical API - Public Access",
        "version": "1.0.0", 
        "status": "ready",
        "note": "Models load on first request for better startup time",
        "endpoints": {
            "medical_ner_en": "POST /extract",
            "medical_ner_es": "POST /extractEs", 
            "similarity_search": "POST /similar_db",
            "health_check": "GET /similarity/health",
            "stats": "GET /similarity/stats",
            "documentation": "GET /docs"
        }
    }

@app.post("/extract", response_model=TextEntities)
def extract_entities(input_data: TextInput):
    """Extract medical entities from English text"""
    try:
        validate_text_input(input_data.text)
        
        logger.info(f"Processing NER request (EN): {input_data.text[:50]}...")
        # La primera vez cargará el modelo
        entities_raw = extract_medical_terms(input_data.text)
        entities = [Entity(**e) for e in entities_raw]
        logger.info(f"Found {len(entities)} entities")
        return TextEntities(entities=entities)
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in extract_entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extractEs", response_model=TextEntities)
def extract_entities_es(input_data: TextInput):
    """Extract medical entities from Spanish text - No authentication required"""
    try:
        logger.info(f"Processing NER request (ES): {input_data.text[:50]}...")
        entities_raw = extract_medical_terms_es(input_data.text)
        entities = [Entity(**e) for e in entities_raw]
        logger.info(f"Found {len(entities)} entities")
        return TextEntities(entities=entities)
    except Exception as e:
        logger.error(f"Error in extract_entities_es: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/similar_db", response_model=SimilarTermList)
def similar_terms_db(input_data: SimilarTermInput):
    """Find similar medical terms in OMOP database - No authentication required"""
    try:
        logger.info(f"Processing similarity search for: {input_data.term}")
        raw_results = get_similar_terms_bd(input_data.term)
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
        logger.info(f"Found {len(results)} similar terms")
        return SimilarTermList(results=results)
    except Exception as e:
        logger.error(f"Error in similar_terms_db: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/similarity/health")
def similarity_health():
    """Health check for similarity service"""
    try:
        stats = get_similarity_stats()
        return {
            "status": "healthy",
            "service": "medical_similarity",
            "stats": stats,
            "authentication": "none"
        }
    except Exception as e:
        logger.error(f"Error in similarity_health: {e}")
        return {
            "status": "unhealthy",
            "service": "medical_similarity",
            "error": str(e)
        }

@app.get("/similarity/stats")
def similarity_statistics():
    """Get similarity service statistics"""
    try:
        stats = get_similarity_stats()
        return {
            "stats": stats,
            "note": "Public API - no authentication required"
        }
    except Exception as e:
        logger.error(f"Error in similarity_stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """General health check"""
    return {
        "status": "healthy", 
        "service": "cortex-medical-api",
        "version": "1.0.0",
        "authentication": "none",
        "public_access": True
    }

@app.get("/info")
def project_info():
    """Information about the Cortex project"""
    return {
        "project": "Cortex Medical API",
        "description": "Clinical text processing API for NER and entity linking",
        "research": "Part of clinical text-to-SQL generation research",
        "models": {
            "ner_en": "Helios9/BIOMed_NER",
            "ner_es": "lcampillos/roberta-es-clinical-trials-ner", 
            "embeddings": "pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb"
        },
        "terminologies": ["OMOP CDM", "SNOMED CT"],
        "languages": ["English", "Spanish"],
        "access": "Public - no authentication required"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

# Y también añade esta línea al principio después de crear la app:
# app = FastAPI(...)  # tu app existente
# Añadir:
__all__ = ["app"]