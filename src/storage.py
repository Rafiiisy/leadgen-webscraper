import os
import json

RAW_DIR = "rag_storage/raw"

def get_raw_path(domain):
    name = domain.replace("https://", "").replace("http://", "").replace("/", "_")
    return os.path.join(RAW_DIR, f"{name}.txt")

def save_raw_text(domain, text):
    os.makedirs(RAW_DIR, exist_ok=True)

    # If saving a list of chunks, serialize it
    if isinstance(text, list):
        formatted = json.dumps(text, indent=2, ensure_ascii=False)
    elif isinstance(text, str):
        formatted = text
    else:
        raise ValueError("Text must be a string or list of dicts")

    with open(get_raw_path(domain), "w", encoding="utf-8") as f:
        f.write(formatted)

def load_raw_text(domain):
    path = get_raw_path(domain)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None
