```markdown
---
title: Cortex Medical API
emoji: 🧬
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
license: mit
tags:
  - medical
  - nlp
  - ner
  - entity-linking
  - clinical
  - omop
  - snomed
short_description: Medical NER and Entity Linking API for clinical text processing
---

# Cortex Medical API

A comprehensive medical Natural Language Processing API providing Named Entity Recognition and Entity Linking for clinical text.

## 🚀 Features

- **Named Entity Recognition (NER)**
  - English medical text processing using `Helios9/BIOMed_NER`
  - Spanish medical text processing using `lcampillos/roberta-es-clinical-trials-ner`

- **Entity Linking**
  - OMOP CDM concept mapping
  - SNOMED CT terminology integration
  - Semantic similarity search using BioBERT embeddings

- **Public API**
  - No authentication required
  - RESTful endpoints
  - Automatic OpenAPI documentation

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/extract` | POST | Extract medical entities from English text |
| `/extractEs` | POST | Extract medical entities from Spanish text |
| `/similar_db` | POST | Find similar terms in OMOP database |
| `/similarity/health` | GET | Health check for similarity service |
| `/similarity/stats` | GET | Service statistics |
| `/docs` | GET | Interactive API documentation |

## 🔧 Usage Examples

### English NER
```bash
curl -X POST "https://your-space.hf.space/extract" \
     -H "Content-Type: application/json" \
     -d '{"text": "Patient diagnosed with diabetes mellitus and hypertension"}'
```

### Spanish NER
```bash
curl -X POST "https://your-space.hf.space/extractEs" \
     -H "Content-Type: application/json" \
     -d '{"text": "Paciente diagnosticado con diabetes mellitus e hipertensión"}'
```

### Entity Linking
```bash
curl -X POST "https://your-space.hf.space/similar_db" \
     -H "Content-Type: application/json" \
     -d '{"term": "diabetes"}'
```

## 🔬 Research Context

This API is part of the **Cortex** research project focused on clinical text-to-SQL generation using Large Language Models. The system enables natural language queries over clinical databases structured according to the OMOP Common Data Model.

## 📊 Data Sources

- **OMOP CDM v5.3**: Observational Medical Outcomes Partnership Common Data Model
- **SNOMED CT**: Systematized Nomenclature of Medicine Clinical Terms
- **BioBERT**: Biomedical language representation model

## 🏥 Applications

- Clinical research and epidemiology
- Electronic health record analysis
- Medical terminology standardization
- Clinical decision support systems

## 📜 License

MIT License - Free for research and commercial use.
```