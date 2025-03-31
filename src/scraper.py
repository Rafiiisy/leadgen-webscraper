import re
import cloudscraper
from bs4 import BeautifulSoup
from typing import List, Dict

SECTION_HEADERS = ["h1", "h2", "h3"]
BOILERPLATE_PATTERNS = [
    r"accept cookies?",
    r"terms of use",
    r"privacy policy",
    r"all rights reserved",
    r"copyright \d{4}",
    r"^sign in$|^log in$",
]

SECTION_KEYWORDS = {
    # Mission/About
    "mission": "Mission",
    "our mission": "Mission",
    "purpose": "Mission",
    "core values": "Mission",

    "vision": "About",
    "about": "About",
    "about us": "About",
    "who we are": "About",
    "our story": "About",
    "overview": "About",
    "history": "About",

    # Services / Process
    "services": "Services",
    "solutions": "Services",
    "offerings": "Services",
    "what we do": "Services",
    "capabilities": "Services",
    "expertise": "Services",

    "how it works": "Process",
    "our process": "Process",
    "methodology": "Process",

    # Contact
    "contact": "Contact",
    "contact us": "Contact",
    "get in touch": "Contact",
    "reach out": "Contact",

    # Team / Careers
    "team": "Team",
    "our team": "Team",
    "meet the team": "Team",
    "leadership": "Team",
    "founders": "Team",
    "board of directors": "Team",

    "careers": "Careers",
    "jobs": "Careers",
    "join our team": "Careers",
    "we're hiring": "Careers",
    "opportunities": "Careers",

    # CTA
    "get started": "CTA",
    "request a quote": "CTA",
    "get a quote": "CTA",
    "start now": "CTA",
    "sign up": "CTA",
    "subscribe": "CTA",
    "download now": "CTA",

    # Pricing / Plans
    "pricing": "Pricing",
    "plans": "Pricing",
    "packages": "Pricing",
    "rates": "Pricing",
    "fees": "Pricing",
}

MAX_CHUNKS_PER_LABEL = 10

def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text.strip())    
    # Remove repeated phrases like "Who We Are Who We Are"
    text = re.sub(r'\b(\w+(?: \w+){0,4})\b(?: \1\b){1,}', r'\1', text, flags=re.IGNORECASE)
    return text.strip()


def is_boilerplate(text: str) -> bool:
    text = text.lower().strip()
    if len(text) < 5:
        return True
    return any(re.search(pat, text) for pat in BOILERPLATE_PATTERNS)

def detect_section_label(full_block_text: str) -> str:
    lines = full_block_text.splitlines()
    text = full_block_text.strip()

    # 📣 CTA: short, all-uppercase line
    for line in lines:
        if line.isupper() and len(line.split()) <= 6:
            return "CTA"

    lowered = text.lower()

    # 📧 Email
    if re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text):
        return "Contact"

    # 📞 Phone number
    if re.search(r"\+?\d[\d\s\-().]{7,}\d", text):
        return "Contact"

    # 📍 Location / Address
    if re.search(r"\b(Jl\.?\s+[A-Z])|\b(Street|St\.|Road|Blvd|Avenue|Ave\.|Suite|Building)\b", text, re.IGNORECASE) \
        or re.search(r"\b(Jakarta|Bandung|Surabaya|NY|New York|LA|Los Angeles)\b", text, re.IGNORECASE) \
        or re.search(r"\b\d{5}(-\d{4})?\b", text):
        return "Location"

    # 🌐 Social Media Links
    if re.search(r"https?://(www\.)?(linkedin|facebook|instagram|x|twitter)\.com/\S+", text, re.IGNORECASE):
        return "Social"

    # 💰 Pricing
    if re.search(r"(\$|Rp|IDR|USD)? ?[\d.,]+(k|rb|jt)?", text, re.IGNORECASE):
        return "Pricing"

    # 📅 Schedule / Date / Time
    if re.search(r"\b(Jan(uary)?|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}", text, re.IGNORECASE) \
        or re.search(r"\d{1,2}[:.]?\d{2} ?(AM|PM|WIB)?", text) \
        or re.search(r"(Senin|Selasa|Rabu|Kamis|Jumat|Sabtu|Minggu)", text, re.IGNORECASE):
        return "Schedule"

    # 📝 Careers
    if re.search(r"(join our team|we'?re hiring|open positions|apply now)", lowered):
        return "Careers"

    # 🧪 FAQ
    if re.findall(r"(What|How|Why|Can|Where|Do|Is|Are|When|Who|Should)\b.*\?", text):
        return "FAQ"

    # 🔐 Legal
    if re.search(r"(privacy policy|terms of service|cookies|disclaimer|data policy)", lowered):
        return "Legal"

    # Keyword-based fallback
    for keyword, label in SECTION_KEYWORDS.items():
        if keyword in lowered:
            return label

    # Custom fallback
    if any(k in lowered for k in ["investment", "fund", "capital", "portfolio"]):
        return "Services"

    return "Other"


def extract_semantic_chunks(soup: BeautifulSoup) -> List[Dict]:
    seen_chunks = set()
    final_chunks = []
    chunk_counts: Dict[str, int] = {}

    current_chunk = {
        "title": None,
        "text": []
    }

    for el in soup.body.descendants:
        if not hasattr(el, "name") or el.name is None:
            continue

        text = clean_text(el.get_text(strip=True))
        if not text or is_boilerplate(text):
            continue

        if el.name in SECTION_HEADERS:
            if current_chunk["text"]:
                first_line = current_chunk["text"][0].strip().lower()
                title_line = current_chunk["title"].strip().lower()
                if first_line == title_line:
                    current_chunk["text"] = current_chunk["text"][1:]
                
                unique_lines = []
                seen_lines = set()
                for line in current_chunk["text"]:
                    if line not in seen_lines:
                        unique_lines.append(line)
                        seen_lines.add(line)

                joined_body = " ".join(unique_lines)
                full_text = clean_text(f"{current_chunk['title']}\n{joined_body}")
                label = detect_section_label(full_text)

                if full_text not in seen_chunks and chunk_counts.get(label, 0) < MAX_CHUNKS_PER_LABEL:
                    final_chunks.append({
                        "tag": label,
                        "title": current_chunk["title"],
                        "text": full_text
                    })
                    seen_chunks.add(full_text)
                    chunk_counts[label] = chunk_counts.get(label, 0) + 1

            current_chunk = {
                "title": text,
                "text": []
            }

        elif current_chunk["title"]:
            if text not in current_chunk["text"]:  # avoid intra-chunk duplication
                current_chunk["text"].append(text)

    if current_chunk["title"] and current_chunk["text"]:
        unique_lines = []
        seen_lines = set()
        for line in current_chunk["text"]:
            if line not in seen_lines:
                unique_lines.append(line)
                seen_lines.add(line)

        full_text = f"{current_chunk['title']}\n" + " ".join(unique_lines)
        label = detect_section_label(full_text)

        if full_text not in seen_chunks and chunk_counts.get(label, 0) < MAX_CHUNKS_PER_LABEL:
            final_chunks.append({
                "tag": label,
                "title": current_chunk["title"],
                "text": full_text
            })

    return final_chunks

def scrape_site_structured(domain: str) -> List[Dict]:
    scraper = cloudscraper.create_scraper()
    try:
        response = scraper.get(domain, timeout=10)
        response.raise_for_status()
    except Exception as e:
        return [{"tag": "Error", "title": "", "text": f"Failed to fetch: {e}"}]

    soup = BeautifulSoup(response.text, "html.parser")
    if not soup.body:
        return [{"tag": "Error", "title": "", "text": "No <body> found on page"}]

    return extract_semantic_chunks(soup)
