import pandas as pd
import logging
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
import joblib
from pathlib import Path
from src.utils.preprocess import clean_text

logger = logging.getLogger(__name__)

def load_labels(path="data/labels.csv"):
    """Load and preprocess training labels."""
    if not Path(path).exists():
        raise FileNotFoundError(f"Labels file not found: {path}")
    
    try:
        df = pd.read_csv(path)
        if 'text' not in df.columns or 'category' not in df.columns:
            raise ValueError("CSV must contain 'text' and 'category' columns")
        
        logger.info(f"Loaded {len(df)} training samples")
        df['clean_text'] = df['text'].astype(str).apply(clean_text)
        return df
    except Exception as e:
        logger.error(f"Error loading labels: {e}")
        raise

def train_and_save(output_path="models/tfidf_logreg.joblib"):
    """Train model and save to disk."""
    try:
        Path('models').mkdir(parents=True, exist_ok=True)
        
        logger.info("Loading training data...")
        df = load_labels()
        
        if len(df) < 10:
            raise ValueError(f"Insufficient training data: {len(df)} samples (minimum 10 required)")
        
        X = df['clean_text']
        y = df['category']
        
        logger.info(f"Training set size: {len(X)}, Categories: {y.nunique()}")
        logger.info(f"Category distribution:\n{y.value_counts()}")
        
        # Validate data
        if (X.str.len() == 0).any():
            logger.warning("Some samples have empty text after preprocessing")
            X = X[X.str.len() > 0]
            y = y[X.index]
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,
            random_state=42,
            stratify=y
        )
        
        logger.info(f"Train set: {len(X_train)}, Test set: {len(X_test)}")
        
        logger.info("Building and training pipeline...")
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1, 2), min_df=2)),
            ('clf', LogisticRegression(max_iter=1000, random_state=42))
        ])
        
        pipeline.fit(X_train, y_train)
        
        # Evaluate model
        y_pred = pipeline.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        logger.info(f"Model accuracy: {accuracy:.4f}")
        logger.info("\\nClassification Report:")
        logger.info("\\n" + classification_report(y_test, y_pred))
        
        # Save model
        joblib.dump(pipeline, output_path)
        logger.info(f"Model saved to {output_path}")
        
        return pipeline
    
    except Exception as e:
        logger.error(f"Training failed: {e}")
        raise

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    train_and_save()
