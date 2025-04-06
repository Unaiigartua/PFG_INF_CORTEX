from fastapi import FastAPI
from app.models import TextInput, TextEntities, Entity
from app.ner import extract_medical_terms
from app.similarity import get_similar_terms
from app.similarity_bd import get_similar_terms_bd
from app.models import SimilarTermInput, SimilarTerm, SimilarTermList
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("🔥 Se está ejecutando main.py")

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
        term= str(item["term"]),
        preferred_term=str(item["preferred_term"]),
        concept_id=str(item["concept_id"]),
        similarity=float(item["similarity"]),
        semantic_tag=str(item["semantic_tag"])
    )
    for item in raw_results
]
    return SimilarTermList(results=results)