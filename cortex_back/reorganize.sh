#!/bin/bash

# Script para reorganizar la estructura de cortex_back
# Ejecutar desde el directorio cortex_back/

echo "🔄 Reorganizando estructura de cortex_back..."

# Crear nuevas carpetas
echo "📁 Creando nuevas carpetas..."
mkdir -p app/auth
mkdir -p app/medical
mkdir -p app/core

# Crear archivos __init__.py
echo "📄 Creando archivos __init__.py..."
touch app/auth/__init__.py
touch app/medical/__init__.py
touch app/core/__init__.py

# Mover archivos de autenticación
echo "🔐 Moviendo archivos de autenticación..."
mv app/auth_models.py app/auth/models.py
mv app/auth_schemas.py app/auth/schemas.py
mv app/auth_routes.py app/auth/routes.py
mv app/auth_database.py app/auth/database.py
mv app/security.py app/auth/security.py

# Mover archivos médicos
echo "🏥 Moviendo archivos médicos..."
mv app/ner.py app/medical/ner.py
mv app/nerEs.py app/medical/ner_es.py
mv app/similarity.py app/medical/similarity.py
mv app/similarity_bd.py app/medical/similarity_bd.py
mv app/models.py app/medical/models.py

# Mover archivos de base de datos
echo "💾 Moviendo archivos de base de datos..."
mv app/database.py app/medical/database.py

echo "✅ Reorganización completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Actualizar imports en main.py"
echo "2. Actualizar imports en query_routes.py"
echo "3. Verificar que todo funciona correctamente"