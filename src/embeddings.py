from sentence_transformers import SentenceTransformer

# Load once and reuse across modules
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
