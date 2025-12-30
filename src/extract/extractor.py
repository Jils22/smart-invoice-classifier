import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def extract_text_from_file(filepath: str) -> str:
    """Extract text from file (supports .txt).
    
    Args:
        filepath: Path to the file
    
    Returns:
        Extracted text content
    
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is not supported
    """
    if not isinstance(filepath, str):
        raise TypeError(f"Expected filepath to be str, got {type(filepath).__name__}")
    
    path = Path(filepath)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {filepath}")
    
    # Check file extension
    file_ext = path.suffix.lower()
    if file_ext != '.txt':
        raise ValueError(f"Unsupported file format: {file_ext}. Only .txt files are supported.")
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        
        if not text:
            logger.warning(f"File is empty: {filepath}")
        else:
            logger.debug(f"Extracted {len(text)} characters from {filepath}")
        
        return text
    
    except UnicodeDecodeError as e:
        logger.error(f"Encoding error reading file: {e}")
        raise ValueError(f"File encoding error. Please ensure file is UTF-8 encoded.")
    except Exception as e:
        logger.error(f"Error reading file {filepath}: {e}")
        raise
