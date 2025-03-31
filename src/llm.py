import os
import requests
import threading
from typing import List, Dict
from dotenv import load_dotenv

# 🔐 Load .env API key and model
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(dotenv_path=env_path)

HF_API_KEY_LLM2 = os.getenv("HF_API_KEY_LLM2")
print("🔑 Loaded API Key Prefix:", HF_API_KEY_LLM2[:10])

API_LLM2_URL = f"https://api-inference.huggingface.co/models/google/flan-t5-large"
headers_llm2 = {"Authorization": f"Bearer {HF_API_KEY_LLM2}"}

# 🔒 Thread lock for thread-safe API usage
llm_lock = threading.Lock()

# =============================
# 💬 LLM Answer Generator (Layer 2)
# =============================

def build_llm2_prompt(task: str, chunks: List[Dict[str, str]]) -> str:
    """
    Create a clean summarization prompt for the LLM with no headers or titles.
    """
    context = "\n\n".join(
        chunk["text"].replace(chunk.get("title", ""), "").strip()
        for chunk in chunks if chunk.get("text")
    )

    return f"""Your job is to respond to the given task using only the provided context.

Task:
{task}

Context:
{context}

Begin your answer below:"""

def query_llm(prompt: str, max_length: int = 120, min_length: int = 30, retries: int = 3) -> str:
    """
    Queries Hugging Face summarization model using facebook/bart-large-cnn.
    """
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": max_length,
            "min_length": min_length,
            "do_sample": False
        }
    }

    for attempt in range(1, retries + 1):
        try:
            with llm_lock:
                response = requests.post(API_LLM2_URL, headers=headers_llm2, json=payload)
                response.raise_for_status()
                output = response.json()

            if isinstance(output, list) and 'generated_text' in output[0]:
                return output[0]['generated_text'].strip()
           
        except requests.exceptions.HTTPError as e:
            print(f"🔁 Retry {attempt}/{retries} after HTTP error:\n{e}")
        except requests.exceptions.RequestException as e:
            print(f"🔁 Retry {attempt}/{retries} after request failure:\n{e}")
        except Exception as e:
            print(f"🔁 Retry {attempt}/{retries} after unexpected error:\n{e}")

    return "[Error] Failed to get response from LLM after retries."
