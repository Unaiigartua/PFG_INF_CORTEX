# Dockerfile para el backend FastAPI
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar dependencias adicionales que pueden faltar
RUN pip install email-validator pyarrow

# Copiar el código de la aplicación
COPY . .

# Fix para OllamaClient - usar variable de entorno
RUN sed -i 's|def __init__(self, base_url: str = "http://localhost:11434"):|def __init__(self, base_url: str = None):|' /app/app/sql_generation/ollama_client.py
RUN sed -i '/def __init__(self, base_url: str = None):/a\\        if base_url is None:\n            import os\n            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")' /app/app/sql_generation/ollama_client.py

# Crear directorios necesarios
RUN mkdir -p /app/data \
    /app/OMOP_SNOMED \
    /app/omop_testing \
    /app/rag_index

# Exponer el puerto
EXPOSE 8000

# Variables de entorno
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]