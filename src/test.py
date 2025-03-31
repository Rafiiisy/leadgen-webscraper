import os
import sys
from dotenv import load_dotenv

# 🔐 Load .env API key and model
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(dotenv_path=env_path)
HF_API_KEY_LLM2 = os.getenv("HF_API_KEY_LLM2")
print("🔑 Loaded API Key Prefix:", HF_API_KEY_LLM2[:10])
