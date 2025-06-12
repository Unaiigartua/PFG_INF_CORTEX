import re
from typing import List, Dict, Any

def validate_text_input(text: str, max_length: int = 10000) -> bool:
    """
    Validate text input for medical processing
    
    Args:
        text: Input text to validate
        max_length: Maximum allowed text length
        
    Returns:
        bool: True if valid, raises ValueError if invalid
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    if len(text) > max_length:
        raise ValueError(f"Text too long. Maximum length: {max_length}")
    
    # Check for potentially harmful content
    if re.search(r'<script|javascript:|on\w+\s*=', text, re.IGNORECASE):
        raise ValueError("Text contains potentially harmful content")
    
    return True

def format_similarity_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format similarity search results for API response
    
    Args:
        results: Raw similarity results
        
    Returns:
        List of formatted results
    """
    formatted = []
    for result in results:
        formatted_result = {
            "term": str(result.get("term", "")),
            "preferred_term": str(result.get("preferred_term", "")),
            "concept_id": str(result.get("concept_id", "")),
            "similarity": round(float(result.get("similarity", 0.0)), 4),
            "semantic_tag": str(result.get("semantic_tag", ""))
        }
        formatted.append(formatted_result)
    
    return formatted

def clean_medical_text(text: str) -> str:
    """
    Clean medical text for processing
    
    Args:
        text: Input medical text
        
    Returns:
        Cleaned text
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters that might interfere with processing
    text = re.sub(r'[^\w\s\-\.,;:()\[\]\/]', '', text)
    
    return text