import joblib
from src.utils.preprocess import clean_text
import os

MODEL_PATH = "models/tfidf_logreg.joblib"

def load_model(path=MODEL_PATH):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model not found at {path}. Please train first.")
    return joblib.load(path)

def predict_text(text: str, model=None):
    if model is None:
        model = load_model()
    cleaned = clean_text(text)
    proba = model.predict_proba([cleaned])[0]
    idx = proba.argmax()
    label = model.classes_[idx]
    confidence = float(proba[idx])
    return {"predictedCategory": label, "confidence": confidence}
