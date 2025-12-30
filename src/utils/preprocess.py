import re
import logging
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

logger = logging.getLogger(__name__)

# Cache NLTK resources
_NLTK_INITIALIZED = False
_STOP_WORDS = None
_LEMMATIZER = None

def _ensure_nltk_resources():
    """Download required NLTK resources if not already present."""
    global _NLTK_INITIALIZED, _STOP_WORDS, _LEMMATIZER
    
    if _NLTK_INITIALIZED:
        return
    
    resources = {
        'tokenizers/punkt': 'punkt',
        'corpora/stopwords': 'stopwords',
        'corpora/wordnet': 'wordnet'
    }
    
    for resource_path, resource_name in resources.items():
        try:
            nltk.data.find(resource_path)
        except LookupError:
            logger.info(f"Downloading NLTK resource: {resource_name}")
            try:
                nltk.download(resource_name, quiet=True)
            except Exception as e:
                logger.error(f"Failed to download {resource_name}: {e}")
                raise RuntimeError(f"Failed to download required NLTK resource: {resource_name}")
    
    _STOP_WORDS = set(stopwords.words('english'))
    _LEMMATIZER = WordNetLemmatizer()
    _NLTK_INITIALIZED = True
    logger.info("NLTK resources initialized")

def get_stop_words():
    """Get cached stop words set."""
    global _STOP_WORDS
    if _STOP_WORDS is None:
        _ensure_nltk_resources()
    return _STOP_WORDS

def get_lemmatizer():
    """Get cached lemmatizer instance."""
    global _LEMMATIZER
    if _LEMMATIZER is None:
        _ensure_nltk_resources()
    return _LEMMATIZER

def clean_text(text: str) -> str:
    """Clean and preprocess text for ML model.
    
    Args:
        text: Raw text to clean
    
    Returns:
        Cleaned and preprocessed text
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected text to be str, got {type(text).__name__}")
    
    try:
        # Lowercase
        text = text.lower()
        
        # Remove common invoice-specific terms
        text = re.sub(r'\b(invoice id|invoice|account no:|account)\b', ' ', text)
        
        # Remove special characters, keep only alphanumeric and spaces
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Tokenize
        tokens = nltk.word_tokenize(text)
        
        # Remove stopwords and short tokens
        stop_words = get_stop_words()
        tokens = [t for t in tokens if t not in stop_words and len(t) > 1]
        
        # Lemmatize
        lemmatizer = get_lemmatizer()
        tokens = [lemmatizer.lemmatize(t) for t in tokens]
        
        result = " ".join(tokens)
        logger.debug(f"Cleaned text: {len(text)} -> {len(result)} characters, {len(tokens)} tokens")
        return result
    
    except Exception as e:
        logger.error(f"Error cleaning text: {e}")
        raise
