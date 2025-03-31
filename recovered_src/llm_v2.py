import os
import sys
import requests
import threading
from dotenv import load_dotenv
from typing import List, Dict

# 👇 Ensure project root is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config  # make sure config.HF_MODEL_LLM2_NAME = "facebook/bart-large-cnn"

# 🔐 Load API key and endpoint
load_dotenv()
HF_API_KEY_LLM2 = os.getenv("HF_API_KEY_LLM2")
API_LLM2_URL = f"https://api-inference.huggingface.co/models/{config.HF_MODEL_LLM2_NAME}"
headers_llm2 = {"Authorization": f"Bearer {HF_API_KEY_LLM2}"}

# 🔒 Thread lock for thread-safe API usage
llm_lock = threading.Lock()

# =============================
# 💬 LLM Answer Generator (Layer 2)
# =============================

def build_llm2_prompt(task: str, chunks: List[Dict[str, str]]) -> str:
    """
    Prompt for summarization or Q&A with plain-text output and paraphrasing.
    """
    context = "\n\n".join(
    "\n".join(chunk["text"].splitlines()[1:]).strip()
    for chunk in chunks if chunk.get("text")
)



    return f"""\
Give an answer to the task and paraphrase the given context concisely.

Task:
{task}

Context:
{context}


Begin your answer below:
"""


def query_llm(prompt: str, max_length: int = 120, min_length: int = 30, retries: int = 3) -> str:
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_length,
            "temperature": 0.7,
            "top_p": 0.9,
            "do_sample": True,
            "repetition_penalty": 1.1
        }
    }

    for attempt in range(1, retries + 1):
        try:
            with llm_lock:
                response = requests.post(API_LLM2_URL, headers=headers_llm2, json=payload)
                response.raise_for_status()
                output = response.json()  # This is typically a list of dicts

            # -- Attempt to extract text properly --
            if isinstance(output, list) and len(output) > 0 and isinstance(output[0], dict):
                # 1) If Hugging Face summarization pipeline -> 'summary_text'
                if 'summary_text' in output[0]:
                    return output[0]['summary_text'].strip()
                # 2) If some generation pipeline -> 'generated_text'
                elif 'generated_text' in output[0]:
                    return output[0]['generated_text'].strip()
            
            # If none of the known keys are found, just return the raw string
            return str(output)

        except requests.exceptions.HTTPError as e:
            print(f"🔁 Retry {attempt}/{retries} after HTTP error:\n{e}")
        except requests.exceptions.RequestException as e:
            print(f"🔁 Retry {attempt}/{retries} after request failure:\n{e}")
        except Exception as e:
            print(f"🔁 Retry {attempt}/{retries} after unexpected error:\n{e}")

    return "[Error] Failed to get response from LLM after retries."