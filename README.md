# Smart Invoice Classifier

A production-ready ML-based invoice classifier with TF-IDF + Logistic Regression, Flask REST API, and SQLite database.

## 🚀 Features

- **Text Extraction**: Extracts text from invoice documents (.txt format)
- **ML Classification**: TF-IDF vectorization + Logistic Regression model
- **REST API**: Flask-based API for upload and classification
- **Database**: SQLite storage for classified invoices
- **Error Handling**: Comprehensive validation and error management
- **Logging**: Structured logging across all modules
- **Health Checks**: API monitoring endpoint
- **Production Ready**: Debug mode disabled, proper security

## 📁 Project Structure

```
smart-invoice-classifier/
├── main.py                          # Pipeline orchestration
├── requirements.txt                 # Python dependencies
├── .env.example                     # Configuration template
├── .gitignore                       # Git ignore rules
├── README.md                        # This file
├── src/
│   ├── api/
│   │   └── app.py                  # Flask REST API
│   ├── database/
│   │   └── db.py                   # SQLite operations
│   ├── extract/
│   │   └── extractor.py            # Text extraction
│   ├── model/
│   │   ├── train.py                # Model training
│   │   └── predict.py              # Inference
│   └── utils/
│       └── preprocess.py           # Text preprocessing
├── data/
│   ├── generate_dummy_invoices.py  # Generate test data
│   ├── labels.csv                  # Training labels
│   └── dummy_invoices/             # Test files (git-ignored)
├── models/                          # Trained models (git-ignored)
└── notebook/
    └── Smart_Invoice_Classifier.ipynb
```

## 🔧 Installation

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/smart-invoice-classifier.git
cd smart-invoice-classifier
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings if needed
```

## 📖 Usage

### Quick Start - Run Full Pipeline
```bash
python main.py
```
This will:
1. Generate dummy training data
2. Train the ML model
3. Start the Flask API server

### Individual Steps

**Generate Test Data:**
```bash
python data/generate_dummy_invoices.py
```

**Train Model:**
```bash
python src/model/train.py
```

**Start API:**
```bash
python src/api/app.py
# API runs at http://localhost:5000
```

## 🌐 API Endpoints

### POST /upload
Upload and classify an invoice

**Request:**
```bash
curl -F "invoiceFile=@invoice.txt" http://localhost:5000/upload
```

**Response:**
```json
{
  "invoiceId": "550e8400-e29b-41d4-a716-446655440000",
  "fileName": "invoice.txt",
  "predictedCategory": "Utilities",
  "confidenceScore": 0.91,
  "createdAt": "2025-12-30T12:00:00Z"
}
```

### GET /classified?limit=100
Retrieve classified invoices

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "fileName": "invoice.txt",
    "extractedText": "...",
    "predictedCategory": "Utilities",
    "confidenceScore": 0.91,
    "createdAt": "2025-12-30T12:00:00Z"
  }
]
```

**Parameters:**
- `limit` (optional): Number of results (1-1000, default: 100)

### GET /health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true
}
```

## ⚙️ Configuration

Create a `.env` file from `.env.example`:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=False
FLASK_PORT=5000

# Database
DB_PATH=invoices.db

# File Upload
UPLOAD_DIR=invoices_uploads
MAX_UPLOAD_SIZE=10485760  # 10MB

# Model
MODEL_PATH=models/tfidf_logreg.joblib
```

## 📊 Model Details

| Component | Details |
|-----------|---------|
| **Algorithm** | Logistic Regression |
| **Vectorizer** | TF-IDF |
| **Max Features** | 5000 |
| **N-grams** | 1-2 words |
| **Train/Test Split** | 80/20 |
| **Model File** | models/tfidf_logreg.joblib |

## 🔐 Error Handling

All endpoints include comprehensive error handling:

| Status | Meaning | Example |
|--------|---------|---------|
| 200 | Success | Classification complete |
| 400 | Bad Request | Missing file, invalid format |
| 404 | Not Found | Endpoint doesn't exist |
| 413 | Payload Too Large | File > 10MB |
| 500 | Server Error | Processing failed |
| 503 | Unavailable | Model not loaded |

## 📝 Logging

The application logs all operations with timestamps. To configure:

**Edit src/api/app.py:**
```python
logging.basicConfig(
    level=logging.INFO,  # or DEBUG for verbose
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),  # Add file logging
        logging.StreamHandler()
    ]
)
```

## 🗄️ Database

SQLite database schema:

```sql
CREATE TABLE invoices (
    id TEXT PRIMARY KEY,
    fileName TEXT NOT NULL,
    extractedText TEXT,
    predictedCategory TEXT NOT NULL,
    confidenceScore REAL NOT NULL,
    createdAt TEXT NOT NULL
)
```

**Indexes:**
- `idx_createdAt` on `createdAt DESC` for fast queries

**Helper Functions:**
- `get_all(limit=100)` - Retrieve recent invoices
- `get_by_id(invoice_id)` - Get specific invoice
- `count_invoices()` - Total count
- `insert_invoice(row)` - Insert/update invoice

## 🐛 Troubleshooting

### Model Not Found
```
FileNotFoundError: Model not found at models/tfidf_logreg.joblib
```
**Solution:** Train the model first
```bash
python src/model/train.py
```

### Port Already in Use
**Solution:** Change port in `.env` or kill existing process

### File Upload Fails
- ✅ Check file is `.txt` format
- ✅ Verify file size < 10MB
- ✅ Ensure UTF-8 encoding

### NLTK Resources Missing
**Solution:** Automatically downloaded on first use. Check console output.

## 🔒 Security

- ✅ File extension validation
- ✅ File size limits (10MB max)
- ✅ Filename sanitization
- ✅ Temporary file cleanup
- ✅ Debug mode disabled in production
- ✅ Proper error messages (no sensitive data leaked)

## 📦 Dependencies

See `requirements.txt`:
- Flask 2.3.2
- scikit-learn 1.2.2
- pandas 2.1.2
- nltk 3.8.1
- gunicorn 20.1.0

## 🚀 Deployment

### Using Gunicorn
```bash
gunicorn --workers 4 --bind 0.0.0.0:5000 src.api.app:app
```

### Docker (Optional)
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "src.api.app:app"]
```

## 🧪 Testing

### Manual API Test
```bash
# Health check
curl http://localhost:5000/health

# Upload file
curl -F "invoiceFile=@data/dummy_invoices/INV0001.txt" \
  http://localhost:5000/upload

# Get results
curl "http://localhost:5000/classified?limit=10"
```

## 💡 Performance Tips

1. **Faster Inference**: Model cached in memory after first load
2. **Faster Queries**: Database indexed on creation date
3. **Efficient Processing**: NLTK resources cached after download
4. **Resource Usage**: Uses sparse matrices for TF-IDF

## 📚 Additional Resources

- [Scikit-learn Documentation](https://scikit-learn.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [NLTK Documentation](https://www.nltk.org/)

## 📄 License

[Your License Here]

## 👤 Author

[Your Name/Organization]

## ❓ Support

For issues and questions, please:
1. Check the troubleshooting section
2. Review application logs
3. Create a GitHub issue with:
   - Error message
   - Steps to reproduce
   - Python version
   - OS information

---

**Last Updated:** December 30, 2025  
**Python Version:** 3.8+
