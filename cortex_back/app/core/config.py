import os
from pathlib import Path

# Rutas base adaptadas para Docker
BASE_DIR = Path("/app")  # En Docker, trabajamos desde /app
DATA_DIR = BASE_DIR / "data"
OMOP_DIR = BASE_DIR / "OMOP_SNOMED"  # Aquí están todos tus archivos
OMOP_TESTING_DIR = BASE_DIR / "omop_testing"
RAG_INDEX_DIR = BASE_DIR / "rag_index"
MODEL_CACHE_DIR = BASE_DIR / "model_cache"

# Crear directorios si no existen (solo los que podrían no estar)
for dir_path in [OMOP_TESTING_DIR, RAG_INDEX_DIR, MODEL_CACHE_DIR]:
    dir_path.mkdir(exist_ok=True, parents=True)

# Configuración Ollama (usar el servicio Docker)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-coder-v2:16b-lite-instruct-q4_K_M")

# Rutas específicas de archivos que ya tienes
DATASET_PATH = str(BASE_DIR / "text2sql_epi_dataset_omop.xlsx")
OMOP_SCHEMA_PATH = str(BASE_DIR / "omop_schema_stub.txt")

# Base de datos de testing (se creará si no existe)
OMOP_DB_PATH = str(OMOP_TESTING_DIR / "omop_complete.db")

# Rutas para entity linking (ya existen en tu OMOP_SNOMED)
FAISS_INDEX_PATH = str(OMOP_DIR / "faiss_snomed.index")
ID_MAPPING_PATH = str(OMOP_DIR / "concept_ids.pkl")
SYNONYMS_PATH = str(OMOP_DIR / "synonyms.parquet")
OMOP_CONCEPTS_DB = str(OMOP_DIR / "omop_snomed.db")  # Tu DB existente

# Base de datos de autenticación
AUTH_DB_PATH = str(DATA_DIR / "auth.db")