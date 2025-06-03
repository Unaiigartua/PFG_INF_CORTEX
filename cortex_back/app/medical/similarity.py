from urllib.request import urlopen, Request
from urllib.parse import quote
import json
import torch
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModel

# User-Agent personalizado para evitar bloqueo
user_agent = "Mozilla/5.0"

def urlopen_with_header(url):
    req = Request(url)
    req.add_header('User-Agent', user_agent)
    return urlopen(req)

def getSnomedCodeSimilar(searchTerm):
    encoded_term = quote(searchTerm)
    url = f"https://snowstorm-training.snomedtools.org/snowstorm/snomed-ct/browser/MAIN/descriptions?term={encoded_term}&active=true&conceptActive=true&groupByConcept=false&searchMode=STANDARD&offset=0&limit=50"
    response = urlopen_with_header(url).read()
    data = json.loads(response.decode('utf-8'))

    results = []
    for term in data['items']:

        results.append({
            "term": term['term'],
            "preferred_term": term['concept']['pt']['term'],
            "concept_id": term['concept']['conceptId'],
            "fsn": term['concept']['fsn']['term'],
        })
    return results

# Load BioBERT once
model_name = "dmis-lab/biobert-v1.1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def get_mean_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    embeddings = outputs.last_hidden_state
    attention_mask = inputs["attention_mask"]
    mask_expanded = attention_mask.unsqueeze(-1).expand(embeddings.size()).float()
    summed = torch.sum(masked_embeddings := embeddings * mask_expanded, dim=1)
    counts = torch.clamp(mask_expanded.sum(dim=1), min=1e-9)
    return summed / counts

def get_similar_terms(term):
    original_emb = get_mean_embedding(term)
    candidates = getSnomedCodeSimilar(term)

    for c in candidates:
        candidate_emb = get_mean_embedding(c["term"])
        sim = cosine_similarity(original_emb.numpy(), candidate_emb.numpy())[0][0]
        c["similarity"] = sim


        fsn = c.get("fsn")
        if fsn and "(" in fsn and ")" in fsn:
            c["semantic_tag"] = fsn.split("(")[-1].replace(")", "").strip()
        else:
            c["semantic_tag"] = "Unknown"


    return sorted(candidates, key=lambda x: x["similarity"], reverse=True)
