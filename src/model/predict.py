import joblib
import logging
from pathlib import Path
from src.utils.preprocess import clean_text

logger = logging.getLogger(__name__)

MODEL_PATH = "models/tfidf_logreg.joblib"

def load_model(path=MODEL_PATH):
    """Load trained model from disk."""
    model_path = Path(path)
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found at {path}. Please train first using src/model/train.py")
    
    try:
        model = joblib.load(path)
        logger.info(f"Model loaded successfully from {path}")
        return model
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise

def predict_text(text: str, model=None):
    """Predict invoice category from text.
    
    Args:
        text: Input text to classify
        model: Trained model (optional, will load if None)
    
    Returns:
        dict with 'predictedCategory' and 'confidence' keys
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected text to be str, got {type(text).__name__}")
    
    if not text or len(text.strip()) == 0:
        raise ValueError("Input text cannot be empty")
    
    if model is None:
        model = load_model()
    
    try:
        cleaned = clean_text(text)
        if not cleaned or len(cleaned.strip()) == 0:
            logger.warning("Text is empty after preprocessing")
            return {"predictedCategory": "Unknown", "confidence": 0.0}
        
        proba = model.predict_proba([cleaned])[0]
        idx = proba.argmax()
        label = model.classes_[idx]
        confidence = float(proba[idx])
        
        logger.debug(f"Prediction: {label} (confidence: {confidence:.4f})")
        return {"predictedCategory": label, "confidence": confidence}
    
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise
