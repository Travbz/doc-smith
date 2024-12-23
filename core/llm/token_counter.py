from typing import Dict, Optional
import tiktoken
import logging
from ..utils.logging_config import setup_logger

logger = setup_logger(__name__)

# Cache encoding instances
_ENCODERS: Dict[str, tiktoken.Encoding] = {}

def get_encoder(model: str) -> tiktoken.Encoding:
    """Get or create a cached encoder for the specified model."""
    if model not in _ENCODERS:
        try:
            _ENCODERS[model] = tiktoken.encoding_for_model(model)
        except KeyError:
            logger.warning(f"Model {model} not found, using cl100k_base encoding")
            _ENCODERS[model] = tiktoken.get_encoding("cl100k_base")
    return _ENCODERS[model]

def count_tokens(text: str, model: str) -> int:
    """Count the number of tokens in the text for the specified model."""
    encoder = get_encoder(model)
    return len(encoder.encode(text))

def truncate_to_token_limit(text: str, model: str, max_tokens: int) -> str:
    """Truncate text to fit within the specified token limit."""
    encoder = get_encoder(model)
    tokens = encoder.encode(text)
    
    if len(tokens) <= max_tokens:
        return text
        
    truncated_tokens = tokens[:max_tokens]
    return encoder.decode(truncated_tokens)

def estimate_tokens_from_char_length(char_length: int) -> int:
    """Rough estimate of tokens from character length."""
    # Average ratio of characters to tokens (varies by language and content)
    CHAR_TO_TOKEN_RATIO = 4
    return char_length // CHAR_TO_TOKEN_RATIO

def check_token_limit(text: str, model: str, max_tokens: int) -> bool:
    """Check if text is within token limit."""
    return count_tokens(text, model) <= max_tokens