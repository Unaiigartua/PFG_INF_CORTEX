import sys
from pathlib import Path

# Añadir path para importar app
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test que podemos importar todos los módulos necesarios"""
    try:
        from app.main import app
        print("✅ app.main importado")
        
        from app.auth.models import User, QueryLog
        print("✅ app.auth.models importado")
        
        from app.medical.ner import extract_medical_terms
        print("✅ app.medical.ner importado")
        
        from app.medical.similarity_bd import get_similar_terms_bd
        print("✅ app.medical.similarity_bd importado")
        
        print("\n🎉 Todos los imports funcionan correctamente!")
        return True
        
    except ImportError as e:
        print(f"❌ Error de import: {e}")
        return False

def test_fastapi_app():
    """Test que la app FastAPI funciona"""
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.get("/")
        
        if response.status_code == 200:
            print("✅ FastAPI app responde correctamente")
            print(f"📄 Respuesta: {response.json()}")
            return True
        else:
            print(f"❌ FastAPI app error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testando FastAPI: {e}")
        return False

def main():
    """Ejecutar tests simples"""
    print("🧪 Ejecutando tests simples de verificación...\n")
    
    # Verificar directorio
    if not Path("app").exists():
        print("❌ No se encuentra el directorio 'app'")
        print("💡 Ejecuta desde cortex_back/")
        return False
    
    # Test imports
    if not test_imports():
        return False
    
    print()
    
    # Test FastAPI
    if not test_fastapi_app():
        return False
    
    print("\n🎉 ¡Todos los tests simples pasaron!")
    print("🚀 Ya puedes ejecutar: python run_tests.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)