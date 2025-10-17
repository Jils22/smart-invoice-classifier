import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
import joblib
from src.utils.preprocess import clean_text
import os

def load_labels(path="data/labels.csv"):
    df = pd.read_csv(path)
    df['clean_text'] = df['text'].astype(str).apply(clean_text)
    return df

def train_and_save(output_path="models/tfidf_logreg.joblib"):
    os.makedirs('models', exist_ok=True)
    df = load_labels()
    X = df['clean_text']
    y = df['category']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=5000, ngram_range=(1,2))),
        ('clf', LogisticRegression(max_iter=1000))
    ])
    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)
    print(classification_report(y_test, preds))
    joblib.dump(pipeline, output_path)
    print("Saved model to", output_path)

if __name__ == "__main__":
    train_and_save()
