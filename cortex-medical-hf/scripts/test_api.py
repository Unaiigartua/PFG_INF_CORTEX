#!/usr/bin/env python3
"""
Test script for the Cortex Medical API
"""
import requests
import json

def test_api(base_url="http://localhost:7860"):
    """Test all API endpoints"""
    
    print(f"Testing API at: {base_url}")
    
    # Test root endpoint
    print("\n1. Testing root endpoint...")
    response = requests.get(f"{base_url}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # Test English NER
    print("\n2. Testing English NER...")
    data = {"text": "Patient diagnosed with diabetes mellitus and hypertension"}
    response = requests.post(f"{base_url}/extract", json=data)
    print(f"Status: {response.status_code}")
    print(f"Entities found: {len(response.json()['entities'])}")
    
    # Test Spanish NER
    print("\n3. Testing Spanish NER...")
    data = {"text": "Paciente diagnosticado con diabetes mellitus e hipertensión"}
    response = requests.post(f"{base_url}/extractEs", json=data)
    print(f"Status: {response.status_code}")
    print(f"Entidades encontradas: {len(response.json()['entities'])}")
    
    # Test similarity search
    print("\n4. Testing similarity search...")
    data = {"term": "diabetes"}
    response = requests.post(f"{base_url}/similar_db", json=data)
    print(f"Status: {response.status_code}")
    print(f"Similar terms found: {len(response.json()['results'])}")
    
    # Test health check
    print("\n5. Testing health check...")
    response = requests.get(f"{base_url}/similarity/health")
    print(f"Status: {response.status_code}")
    print(f"Health: {response.json()['status']}")
    
    print("\nAPI testing completed!")

if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:7860"
    test_api(url)