#!/usr/bin/env python3
"""
Script para verificar que todo esté configurado correctamente
"""
import sys
import requests
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

def check_ollama_connection():
    """Verificar conexión con Ollama"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print("✅ Ollama está ejecutándose")
            print(f"   Modelos disponibles: {len(models)}")
            
            # Verificar modelo específico
            target_model = "deepseek-coder-v2:16b-lite-instruct-q4_K_M"
            model_names = [m['name'] for m in models]
            if any(target_model in name for name in model_names):
                print(f"✅ Modelo {target_model} disponible")
            else:
                print(f"❌ Modelo {target_model} no encontrado")
                print(f"   Modelos disponibles: {model_names}")
            return True
        else:
            print(f"❌ Ollama responde con código {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error conectando con Ollama: {e}")
        print("   Asegúrate de que Ollama esté ejecutándose: ollama serve")
        return False

def check_required_files():
    """Verificar archivos necesarios"""
    base_dir = Path(__file__).parent.parent
    
    required_files = [
        "../data/text2sql_epi_dataset_omop.xlsx",
        "../data/omop_schema_stub.txt",
        "../omop_testing/omop_complete.db"
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} no encontrado")
            all_exist = False
    
    return all_exist

def check_python_packages():
    """Verificar paquetes de Python"""
    required_packages = [
        'fastapi', 'uvicorn', 'requests', 'faiss', 
        'sentence_transformers', 'pandas', 'numpy', 'pydantic'
    ]
    
    all_available = True
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} no instalado")
            all_available = False
    
    return all_available

def main():
    print("🔍 Verificando configuración del sistema...")
    print("\n📦 Verificando paquetes de Python:")
    packages_ok = check_python_packages()
    
    print("\n📁 Verificando archivos necesarios:")
    files_ok = check_required_files()
    
    print("\n🤖 Verificando conexión con Ollama:")
    ollama_ok = check_ollama_connection()
    
    print("\n" + "="*50)
    if packages_ok and files_ok and ollama_ok:
        print("🎉 Todo configurado correctamente!")
        print("   Puedes ejecutar: uvicorn app.main:app --reload")
    else:
        print("⚠️  Hay problemas de configuración:")
        if not packages_ok:
            print("   - Instala los paquetes faltantes: pip install -r requirements.txt")
        if not files_ok:
            print("   - Verifica que tengas todos los archivos de datos")
        if not ollama_ok:
            print("   - Inicia Ollama: ollama serve")
            print("   - Descarga el modelo: ollama pull deepseek-coder-v2:16b-lite-instruct-q4_K_M")

if __name__ == "__main__":
    main()