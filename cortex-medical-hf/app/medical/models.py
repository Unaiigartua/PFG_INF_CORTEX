from pydantic import BaseModel
from typing import List

class TextInput(BaseModel):
    text: str

class Entity(BaseModel):
    word: str
    entity_group: str
    score: float
    start: int
    end: int

class TextEntities(BaseModel):
    entities: List[Entity]

class SimilarTermInput(BaseModel):
    term: str

class SimilarTerm(BaseModel):
    term: str
    preferred_term: str
    concept_id: str
    similarity: float
    semantic_tag: str

class SimilarTermList(BaseModel):
    results: List[SimilarTerm]