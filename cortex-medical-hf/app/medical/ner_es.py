from transformers import pipeline

# Variables globales para modelos
_pipe_es = None

def get_pipeline_es():
    """Lazy loading del pipeline de NER en español"""
    global _pipe_es
    if _pipe_es is None:
        model_path = "lcampillos/roberta-es-clinical-trials-ner"
        _pipe_es = pipeline(
            task="ner",
            model=model_path,
            aggregation_strategy="simple"
        )
    return _pipe_es

def merge_consecutive_entities(entities, text):
    entities = sorted(entities, key=lambda x: x['start'])
    merged_entities = []
    current_entity = None

    for entity in entities:
        if current_entity is None:
            current_entity = entity
        elif (
            entity['entity_group'] == current_entity['entity_group'] and
            (entity['start'] <= current_entity['end'])
        ):
            current_entity['end'] = max(current_entity['end'], entity['end'])
            current_entity['word'] = text[current_entity['start']:current_entity['end']]
            current_entity['score'] = (current_entity['score'] + entity['score']) / 2
        else:
            merged_entities.append(current_entity)
            current_entity = entity
    if current_entity:
        merged_entities.append(current_entity)

    return merged_entities

def extract_medical_terms_es(text: str):
    """Extract medical terms using lazy-loaded pipeline"""
    pipe = get_pipeline_es()
    raw_entities = pipe(text)
    return merge_consecutive_entities(raw_entities, text)