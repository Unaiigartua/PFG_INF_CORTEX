#!/bin/bash
# init-data.sh - Script para verificar datos existentes

echo "📊 Verificando datos existentes..."

# Verificar archivos OMOP
echo "Verificando archivos OMOP en cortex_back/app/OMOP_SNOMED/:"
if [ -f "./cortex_back/app/OMOP_SNOMED/CONCEPT.csv" ]; then
    echo "✅ CONCEPT.csv encontrado"
else
    echo "❌ CONCEPT.csv no encontrado"
fi

if [ -f "./cortex_back/app/OMOP_SNOMED/omop_snomed.db" ]; then
    echo "✅ omop_snomed.db encontrado"
else
    echo "❌ omop_snomed.db no encontrado"
fi

if [ -f "./cortex_back/app/OMOP_SNOMED/faiss_snomed.index" ]; then
    echo "✅ faiss_snomed.index encontrado"
else
    echo "❌ faiss_snomed.index no encontrado"
fi

if [ -f "./cortex_back/app/OMOP_SNOMED/concept_ids.pkl" ]; then
    echo "✅ concept_ids.pkl encontrado"
else
    echo "❌ concept_ids.pkl no encontrado"
fi

# Verificar base de datos de auth
if [ -f "./cortex_back/data/auth.db" ]; then
    echo "✅ auth.db encontrado"
else
    echo "⚠️  auth.db no encontrado (se creará automáticamente)"
fi

# Verificar dataset para RAG
if [ -f "./cortex_back/text2sql_epi_dataset_omop.xlsx" ]; then
    echo "✅ Dataset RAG encontrado"
else
    echo "⚠️  text2sql_epi_dataset_omop.xlsx no encontrado"
fi

# Crear directorios adicionales que podrían necesitarse
mkdir -p cortex_back/omop_testing  
mkdir -p cortex_back/rag_index
mkdir -p cortex_back/model_cache

echo ""
echo "📁 Estructura de directorios verificada"
echo "🚀 Los archivos se montarán desde sus ubicaciones actuales"