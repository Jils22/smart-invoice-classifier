import os
import tempfile
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

def ocr_image(image_path):
    return pytesseract.image_to_string(Image.open(image_path))

def extract_text_from_file(filepath: str) -> str:
    """Handle .txt, image files (png/jpg), and PDFs (by converting pages to images)."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(filepath)
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.txt':
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    elif ext in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
        return ocr_image(filepath)
    elif ext == '.pdf':
        text_pages = []
        # convert pdf pages to images using pdf2image (requires poppler)
        with tempfile.TemporaryDirectory() as td:
            images = convert_from_path(filepath, output_folder=td)
            for im in images:
                text_pages.append(pytesseract.image_to_string(im))
        return "\n".join(text_pages)
    else:
        raise ValueError('Unsupported file type for OCR: ' + ext)
