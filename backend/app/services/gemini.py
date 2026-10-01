"""
Shared Gemini client configuration.

Loads the API key from backend/.env and creates a google-genai Client.
This module is reused by embeddings (Step 4) and can be reused by chat later.
"""

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from google import genai

# Load backend/.env (never commit real secrets).
# override=True so changing GEMINI_CHAT_MODEL in .env takes effect after reload.
BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env", override=True)


class GeminiConfigError(Exception):
    """Raised when Gemini environment configuration is missing or invalid."""


def get_gemini_api_key() -> str:
    """Return GEMINI_API_KEY or raise a clear configuration error."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        raise GeminiConfigError(
            "GEMINI_API_KEY is not configured. "
            "Copy backend/.env.example to backend/.env and set your key."
        )
    return api_key


def get_embedding_model() -> str:
    """
    Embedding model name from env.

    Default is Gemini's text embedding model. Override with GEMINI_EMBEDDING_MODEL.
    """
    return os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001").strip()


def get_chat_model() -> str:
    """
    Chat / generation model name from env.

    Used by the RAG answer step. Override with GEMINI_CHAT_MODEL.
    Default uses flash-lite because free-tier quota on larger flash
    models is easy to exhaust during learning/testing.
    """
    return os.getenv("GEMINI_CHAT_MODEL", "gemini-flash-lite-latest").strip()


@lru_cache(maxsize=1)
def get_gemini_client() -> genai.Client:
    """
    Create one shared Gemini client.

    The API key is passed explicitly. We never log or return the key.
    """
    return genai.Client(api_key=get_gemini_api_key())
