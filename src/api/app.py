import os
import logging
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid
from pathlib import Path
from src.extract.extractor import extract_text_from_file
from src.model.predict import load_model, predict_text
from src.database.db import insert_invoice, get_all, ensure_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

UPLOAD_DIR = "invoices_uploads"
ALLOWED_EXTENSIONS = {'txt', 'pdf'}
MAX_FILENAME_LENGTH = 255

Path(UPLOAD_DIR).mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB

model = None
try:
    model = load_model()
    logger.info("Model loaded successfully")
except FileNotFoundError as e:
    logger.warning(f"Model not found: {e}")
except Exception as e:
    logger.error(f"Unexpected error loading model: {e}")

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload():
    """Upload and classify an invoice."""
    try:
        if 'invoiceFile' not in request.files:
            logger.warning("Upload request missing 'invoiceFile' field")
            return jsonify({"error": "No file part 'invoiceFile'"}), 400
        
        f = request.files['invoiceFile']
        if f.filename == '':
            logger.warning("Upload request with empty filename")
            return jsonify({"error": "No selected file"}), 400
        
        if not allowed_file(f.filename):
            logger.warning(f"Upload attempt with disallowed file type: {f.filename}")
            return jsonify({"error": f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
        
        filename = secure_filename(f.filename)
        if len(filename) > MAX_FILENAME_LENGTH:
            filename = filename[:MAX_FILENAME_LENGTH]
        
        temp_path = os.path.join(UPLOAD_DIR, filename)
        f.save(temp_path)
        
        try:
            extracted_text = extract_text_from_file(temp_path)
            if not extracted_text or len(extracted_text.strip()) == 0:
                logger.warning(f"No text extracted from file: {filename}")
                return jsonify({"error": "No text could be extracted from file"}), 400
        except FileNotFoundError:
            logger.error(f"File not found after save: {temp_path}")
            return jsonify({"error": "File upload failed"}), 500
        except Exception as e:
            logger.error(f"Text extraction failed for {filename}: {str(e)}")
            return jsonify({"error": f"Text extraction failed: {str(e)}"}), 500
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError as e:
                    logger.warning(f"Failed to delete temporary file {temp_path}: {e}")
        
        if model is None:
            logger.error("Model not available for prediction")
            return jsonify({"error": "Model not available. Train model first."}), 503
        
        try:
            pred = predict_text(extracted_text, model=model)
        except Exception as e:
            logger.error(f"Prediction failed for {filename}: {str(e)}")
            return jsonify({"error": "Prediction failed"}), 500
        
        invoice_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + "Z"
        
        row = {
            "id": invoice_id,
            "fileName": filename,
            "extractedText": extracted_text[:2000],
            "predictedCategory": pred["predictedCategory"],
            "confidenceScore": float(pred["confidence"]),
            "createdAt": now
        }
        
        try:
            insert_invoice(row)
            logger.info(f"Invoice classified successfully: {invoice_id} -> {pred['predictedCategory']}")
        except Exception as e:
            logger.error(f"Failed to store invoice {invoice_id}: {str(e)}")
            return jsonify({"error": "Failed to store classification result"}), 500
        
        return jsonify({
            "invoiceId": invoice_id,
            "fileName": filename,
            "predictedCategory": row["predictedCategory"],
            "confidenceScore": row["confidenceScore"],
            "createdAt": now
        }), 200
    
    except Exception as e:
        logger.exception(f"Unexpected error in upload endpoint: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/classified', methods=['GET'])
def classified():
    """Get all classified invoices."""
    try:
        limit = request.args.get('limit', 100, type=int)
        if limit < 1 or limit > 1000:
            return jsonify({"error": "Limit must be between 1 and 1000"}), 400
        
        rows = get_all(limit=limit)
        logger.info(f"Retrieved {len(rows)} classified invoices")
        return jsonify(rows), 200
    except Exception as e:
        logger.exception(f"Error retrieving classified invoices: {str(e)}")
        return jsonify({"error": "Failed to retrieve invoices"}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "model_loaded": model is not None}), 200

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error."""
    logger.warning("File upload exceeded maximum size")
    return jsonify({"error": "File too large. Maximum size is 10MB"}), 413

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    try:
        ensure_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        exit(1)
    
    logger.info("Starting Flask API on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
