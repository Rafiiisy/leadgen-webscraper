import os
import pickle
import faiss
import numpy as np
from rank_bm25 import BM25Okapi

# ✅ Try internal or fallback to SentenceTransformer
try:
    from src.embeddings import embedding_model
except ImportError:
    from sentence_transformers import SentenceTransformer
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# ✅ Cache path helper
def get_cache_paths(domain):
    base = domain.replace("https://", "").replace("http://", "").replace("/", "_")
    cache_dir = "cache"
    os.makedirs(cache_dir, exist_ok=True)
    return (
        os.path.join(cache_dir, f"{base}_faiss.index"),
        os.path.join(cache_dir, f"{base}_bm25.pkl"),
        os.path.join(cache_dir, f"{base}_chunks.pkl")
    )

def persist_chunks_to_vectorstore(tagged_chunks: list, domain: str):
    """
    Save structured chunks to FAISS + BM25 + pickle.
    """
    faiss_path, bm25_path, chunks_path = get_cache_paths(domain)

    text_chunks = [
        chunk["text"].strip()
        for chunk in tagged_chunks
        if chunk.get("text") and isinstance(chunk["text"], str) and chunk["text"].strip()
    ]

    if not text_chunks:
        raise ValueError(f"❌ No valid chunks to index for: {domain}")

    # Save raw text chunks
    with open(chunks_path, "wb") as f:
        pickle.dump(text_chunks, f)

    # BM25
    tokenized = [chunk.split() for chunk in text_chunks]
    bm25 = BM25Okapi(tokenized)
    with open(bm25_path, "wb") as f:
        pickle.dump(bm25, f)

    # FAISS
    embeddings = embedding_model.encode(text_chunks)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    faiss.write_index(index, faiss_path)

    print(f"✅ Saved vectorstore for domain: {domain}")

class HybridRetriever:
    def __init__(self, domain: str, chunk_size: int = 3):
        self.domain = domain
        self.chunk_size = chunk_size

        faiss_path, bm25_path, chunks_path = get_cache_paths(domain)

        if os.path.exists(faiss_path) and os.path.exists(bm25_path) and os.path.exists(chunks_path):
            self.faiss_index = faiss.read_index(faiss_path)
            with open(bm25_path, "rb") as f:
                self.bm25 = pickle.load(f)
            with open(chunks_path, "rb") as f:
                self.chunks = pickle.load(f)
        else:
            raise FileNotFoundError(f"⚠️ Preprocessed data for domain '{domain}' not found.")

    def search(self, query: str, top_k: int = 5, mix_ratio: float = 0.5):
        if not self.chunks or not self.faiss_index or not self.bm25:
            raise ValueError("⚠️ Retriever not properly initialized.")

        query_embedding = embedding_model.encode([query])[0]

        # FAISS Similarity
        D, I = self.faiss_index.search(np.array([query_embedding]), top_k)
        faiss_scores = {i: 1.0 / (1.0 + D[0][j]) for j, i in enumerate(I[0])}

        # BM25 Scores
        bm25_scores_array = self.bm25.get_scores(query.split())
        bm25_scores_dict = {i: score for i, score in enumerate(bm25_scores_array)}

        # Combine scores
        merged_scores = {}
        for i in range(len(self.chunks)):
            faiss_score = faiss_scores.get(i, 0.0)
            bm25_score = bm25_scores_dict.get(i, 0.0)
            merged = mix_ratio * faiss_score + (1.0 - mix_ratio) * bm25_score
            if merged > 0:
                merged_scores[i] = merged

        top_hits = sorted(merged_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [self.chunks[i] for i, _ in top_hits]
