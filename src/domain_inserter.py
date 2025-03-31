from src.scraper import scrape_site_structured
from src.vectorstore import persist_chunks_to_vectorstore
from src.storage import save_raw_text

def insert_domain(domain: str):
    print(f"🔍 Scraping domain: {domain}")
    structured_chunks = scrape_site_structured(domain)

    # Check if scraping failed
    if isinstance(structured_chunks, str) and structured_chunks.startswith("[Error]"):
        print(f"⚠️ Failed to scrape: {structured_chunks}")
        return structured_chunks

    # Save raw chunks as text (JSON-compatible structure)
    save_raw_text(domain, structured_chunks)

    # Prepare chunks for vectorstore
    chunks = []
    for chunk in structured_chunks:
        if chunk.get("tag") and chunk.get("text"):
            chunks.append({
                "tag": chunk["tag"],
                "text": chunk["text"].strip()
            })

    if not chunks:
        print("⚠️ No chunks generated from structured scrape.")
        return "[Error] No valid chunks extracted."

    persist_chunks_to_vectorstore(chunks, domain)
    print(f"✅ Domain inserted and preprocessed: {domain}")
    return "success"
