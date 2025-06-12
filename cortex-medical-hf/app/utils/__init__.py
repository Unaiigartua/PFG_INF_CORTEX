try:
    from .helpers import validate_text_input, format_similarity_results
    __all__ = [
        "validate_text_input",
        "format_similarity_results"
    ]
except ImportError:
    # If helpers module is not available, just export empty list
    __all__ = []