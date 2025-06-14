#!/usr/bin/env python3
"""
Script para probar el endpoint de generación SQL
"""
import requests
import json

def test_sql_generation_endpoint():
    """Probar el endpoint de generación SQL con un ejemplo"""
    
    # URL base del API
    base_url = "http://localhost:8000"
    
    # 1. Registrar un usuario de prueba (o usar uno existente)
    register_data = {
        "email": "test_sql@example.com",
        "password": "testpassword123"
    }
    
    try:
        # Intentar registrar (puede fallar si ya existe)
        requests.post(f"{base_url}/auth/register", json=register_data)
    except:
        pass  # Usuario ya existe, continuamos
    
    # 2. Hacer login para obtener token
    login_data = {
        "username": register_data["email"],
        "password": register_data["password"]
    }
    
    response = requests.post(f"{base_url}/auth/login", data=login_data)
    if response.status_code != 200:
        print(f"❌ Error en login: {response.status_code}")
        print(response.text)
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login exitoso")
    
    # 3. Verificar health del servicio SQL
    print("\n🔍 Verificando estado del servicio...")
    health_response = requests.get(f"{base_url}/sql-generation/health")
    if health_response.status_code == 200:
        health_data = health_response.json()
        print(f"Estado: {health_data['status']}")
        print(f"Ollama: {health_data['ollama_running']}")
        print(f"Modelo disponible: {health_data['model_available']}")
        
        if health_data['status'] != 'healthy':
            print("❌ Servicio no está saludable")
            return
    else:
        print("❌ No se pudo verificar el estado del servicio")
        return
    
    # 4. Probar generación SQL
    print("\n🧠 Probando generación SQL...")
    sql_request = {
        "question": "How many patients have diabetes?",
        "medical_terms": [
            {
                "term": "diabetes",
                "concept_id": "201826"
            }
        ]
    }
    
    response = requests.post(
        f"{base_url}/sql-generation/",
        json=sql_request,
        headers=headers,
        timeout=300  # 5 minutos de timeout
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Generación SQL exitosa!")
        print(f"\nPregunta: {result['question']}")
        print(f"Ejecutable: {result['is_executable']}")
        print(f"Intentos: {result['attempts_count']}")
        
        if result['similar_example']:
            print(f"\nEjemplo similar usado:")
            print(f"Score: {result['similar_example']['score']:.3f}")
            print(f"Pregunta: {result['similar_example']['question']}")
        
        print(f"\nSQL generado:")
        print("="*50)
        print(result['generated_sql'])
        print("="*50)
        
        if not result['is_executable']:
            print(f"\n❌ Error: {result['error_message']}")
    else:
        print(f"❌ Error en generación SQL: {response.status_code}")
        print(response.text)

def main():
    print("🧪 Probando endpoint de generación SQL...")
    test_sql_generation_endpoint()

if __name__ == "__main__":
    main()