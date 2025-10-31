# llm_client.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:7b")

def generate_from_ollama(prompt: str, max_tokens: int = 512, temperature: float = 0.2):
    """
    Calls Ollama HTTP /api/generate. Adjust payload per your Ollama version.
    """
    url = OLLAMA_URL.rstrip("/") + "/api/generate"
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        # Optional: "top_p": 0.95, "stop": ["\n\n"]
    }
    resp = requests.post(url, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    # Ollama returns an array of generations or a text field depending on versions.
    # Try parsing robustly:
    if isinstance(data, dict) and "text" in data:
        return data["text"]
    if isinstance(data, dict) and "choices" in data:
        # GPT-style
        return data["choices"][0]["text"]
    # fallback
    return str(data)
