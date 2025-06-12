import requests
import json
import time
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def is_ollama_running(self) -> bool:
        """Verificar si Ollama está ejecutándose"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> list:
        """Listar modelos disponibles en Ollama"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            logger.error(f"Error listando modelos: {e}")
            return []
    
    def generate(self, model_name: str, prompt: str, **kwargs) -> Optional[str]:
        """Generar texto con el modelo especificado"""
        try:
            payload = {
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", 0.05),
                    "top_p": kwargs.get("top_p", 0.9),
                    "repeat_penalty": kwargs.get("repeat_penalty", 1.1),
                    "num_predict": kwargs.get("max_tokens", 400),
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=kwargs.get("timeout", 120)
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip()
            else:
                logger.error(f"Error en Ollama: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error generando con Ollama: {e}")
            return None
    
    def check_model_availability(self, model_name: str) -> bool:
        """Verificar si un modelo específico está disponible"""
        available_models = self.list_models()
        return any(model_name in model for model in available_models)