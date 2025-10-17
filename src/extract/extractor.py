import os

def extract_text_from_file(filepath: str) -> str:
    """Simulated extractor: reads .txt files."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()
