import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid
from src.extract.extractor import extract_text_from_file
from src.model.predict import load_model, predict_text
from src.database.db import insert_invoice, get_all, ensure_db

UPLOAD_DIR = "invoices_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB

model = None
try:
    model = load_model()
except Exception as e:
    print("Model load warning:", e)

@app.route('/upload', methods=['POST'])
def upload():
    if 'invoiceFile' not in request.files:
        return jsonify({"error": "No file part 'invoiceFile'"}), 400
    f = request.files['invoiceFile']
    if f.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(f.filename)
    temp_path = os.path.join(UPLOAD_DIR, filename)
    f.save(temp_path)

    try:
        extracted_text = extract_text_from_file(temp_path)
    except Exception as e:
        if os.path.exists(temp_path): os.remove(temp_path)
        return jsonify({"error": str(e)}), 500

    if model is None:
        return jsonify({"error": "Model not available. Train model first."}), 500

    pred = predict_text(extracted_text, model=model)
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
    insert_invoice(row)

    if os.path.exists(temp_path):
        os.remove(temp_path)

    return jsonify({
        "invoiceId": invoice_id,
        "fileName": filename,
        "predictedCategory": row["predictedCategory"],
        "confidenceScore": row["confidenceScore"],
        "createdAt": now
    }), 200

@app.route('/classified', methods=['GET'])
def classified():
    rows = get_all(limit=200)
    return jsonify(rows), 200

if __name__ == "__main__":
    ensure_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
