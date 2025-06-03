from transformers import pipeline

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

model_path = "Helios9/BIOMed_NER"
pipe = pipeline(
    task="token-classification",
    model=model_path,
    tokenizer=model_path,
    aggregation_strategy="simple"
)

def extract_medical_terms(text: str):
    raw_entities = pipe(text)
    return merge_consecutive_entities(raw_entities, text)
