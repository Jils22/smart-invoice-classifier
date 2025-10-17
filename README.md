# Smart Invoice Classifier

## Summary
A minimal ML-based invoice classifier (TF-IDF + Logistic Regression) with a Flask API and SQLite storage.
The project simulates invoice OCR by reading text files stored in `data/dummy_invoices/`. It also includes
an OCR-capable extractor for PDFs and images (requires system deps).

## Getting started

### Requirements
Python 3.8+, install:
```bash
pip install -r requirements.txt
```

### System deps for OCR (Linux)
```bash
sudo apt install tesseract-ocr poppler-utils
```

Windows: install Tesseract from the UB Mannheim builds and add it to PATH. Install Poppler (for pdf2image) separately.

### Generate dummy invoices
```bash
python data/generate_dummy_invoices.py
# Produces data/dummy_invoices/*.txt and data/labels.csv
```

### Train model
```bash
python src/model/train.py
# Saves model to models/tfidf_logreg.joblib
```

### Run Flask API
```bash
python src/api/app.py
# Server runs at http://127.0.0.1:5000
```

### Endpoints
- `POST /upload` - multipart form `invoiceFile` (file). Response:
```json
{
  "invoiceId": "uuid",
  "fileName": "INV0001.txt",
  "predictedCategory": "Utilities",
  "confidenceScore": 0.91,
  "createdAt": "2025-10-09T11:25:00Z"
}
```

- `GET /classified` - list of recent classified invoices (from SQLite).

## How to submit
- Create a Git repository with this project structure.
- Ensure `data/dummy_invoices/` and `models/` are in `.gitignore`.
- Add a clear commit history with messages describing each step.

## Notes on Security & Privacy
- Uploaded files are stored temporarily in `invoices_uploads/` and deleted after processing.
- `.gitignore` prevents committing local data, DB, and generated models.
- For production: add authentication, TLS, proper encryption for sensitive fields; consider storing only masked vendor/account numbers.
