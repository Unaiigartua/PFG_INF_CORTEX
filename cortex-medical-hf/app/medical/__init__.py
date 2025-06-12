from .ner import extract_medical_terms
from .ner_es import extract_medical_terms_es
from .similarity_bd import get_similar_terms_bd, get_entity_linker, get_similarity_stats
from .models import TextInput, TextEntities, Entity, SimilarTermInput, SimilarTerm, SimilarTermList

__all__ = [
    "extract_medical_terms",
    "extract_medical_terms_es", 
    "get_similar_terms_bd",
    "get_entity_linker",
    "get_similarity_stats",
    "TextInput",
    "TextEntities", 
    "Entity",
    "SimilarTermInput",
    "SimilarTerm",
    "SimilarTermList"
]
