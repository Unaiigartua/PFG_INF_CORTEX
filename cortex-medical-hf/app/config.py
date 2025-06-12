import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# OMOP Database paths
OMOP_DIR = DATA_DIR / "OMOP_SNOMED"
OMOP_DB_PATH = str(OMOP_DIR / "omop_snomed.db")
FAISS_INDEX_PATH = str(OMOP_DIR / "faiss_snomed.index")
ID_MAPPING_PATH = str(OMOP_DIR / "concept_ids.pkl")
SYNONYMS_PATH = str(OMOP_DIR / "synonyms.parquet")

# Model configurations
NER_MODEL_EN = "Helios9/BIOMed_NER"
NER_MODEL_ES = "lcampillos/roberta-es-clinical-trials-ner"
SIMILARITY_MODEL = "pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb"

# API Configuration
API_TITLE = "Cortex Medical API"
API_DESCRIPTION = "Medical NER and Entity Linking API for clinical text processing"
API_VERSION = "1.0.0"

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Check if required files exist
def validate_data_files():
    """Validate that all required data files exist"""
    required_files = [
        OMOP_DB_PATH,
        FAISS_INDEX_PATH, 
        ID_MAPPING_PATH,
        SYNONYMS_PATH
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        raise FileNotFoundError(f"Missing required data files: {missing_files}")
    
    return True
