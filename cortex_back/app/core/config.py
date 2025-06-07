import os
from pathlib import Path

# Rutas base
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAG_INDEX_DIR = DATA_DIR / "rag_index"

# Crear directorios si no existen
DATA_DIR.mkdir(exist_ok=True)
RAG_INDEX_DIR.mkdir(exist_ok=True)

# Configuración Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepseek-coder-v2:16b-lite-instruct-q4_K_M")

# Configuración SQL Generation
SQL_GENERATION_TIMEOUT = int(os.getenv("SQL_GENERATION_TIMEOUT", "180"))  
MAX_SQL_ATTEMPTS = int(os.getenv("MAX_SQL_ATTEMPTS", "3"))

# Configuración RAG
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "1"))
DATASET_PATH = str(BASE_DIR / "text2sql_epi_dataset_omop.xlsx")
OMOP_SCHEMA_PATH = str(BASE_DIR / "omop_schema_stub.txt")

# Base de datos OMOP de prueba
OMOP_DB_PATH = str(BASE_DIR / "omop_testing" / "omop_complete.db")