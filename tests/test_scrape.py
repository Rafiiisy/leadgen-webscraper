
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.scraper import scrape_site_structured

def test_scrape(domain: str):
    print(f"🔍 Scraping: {domain}")
    chunks = scrape_site_structured(domain)

    if not chunks or isinstance(chunks, str):
        print("❌ Failed to scrape or returned error string.")
        print(chunks)
        return

    print(f"✅ Total Chunks: {len(chunks)}\n")
    for i, chunk in enumerate(chunks, 1):
        tag = chunk.get("tag", "Unknown")
        title = chunk.get("title", "")
        text = chunk.get("text", "")[:300].replace("\n", " ") + ("..." if len(chunk.get("text", "")) > 300 else "")
        print(f"[{i}] Tag: {tag} | Title: {title}\n{text}\n")

    # Optional: dump to file
    with open("test_scrape_output.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    print("\n📝 Output saved to test_scrape_output.json")

if __name__ == "__main__":
    # Change to any test site you want
    test_scrape("https://www.capraecapital.com/")
