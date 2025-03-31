import os

def get_cache_paths(domain: str):
    """
    Generate consistent cache file paths for FAISS, BM25, and raw chunks.
    """
    base = domain.replace("https://", "").replace("http://", "").replace("/", "_")
    cache_dir = "cache"
    os.makedirs(cache_dir, exist_ok=True)

    faiss_path = os.path.join(cache_dir, f"{base}_faiss.index")
    bm25_path = os.path.join(cache_dir, f"{base}_bm25.pkl")
    chunks_path = os.path.join(cache_dir, f"{base}_chunks.pkl")

    return faiss_path, bm25_path, chunks_path
