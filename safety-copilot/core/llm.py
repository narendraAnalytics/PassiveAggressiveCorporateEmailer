import os

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

from core.models import DraftResponse, Tone
from core.prompts import SYSTEM_PROMPT, build_user_prompt

load_dotenv()

MODEL_NAME = "gemini-3.6-flash"

_client: genai.Client | None = None


class MissingApiKeyError(RuntimeError):
    """Raised when no Gemini API key is configured."""


def _get_api_key() -> str | None:
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY")


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = _get_api_key()
        if not api_key:
            raise MissingApiKeyError(
                "GEMINI_API_KEY not found. Set it in .env locally, or in "
                "Streamlit Cloud under App settings -> Secrets."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def generate_draft(message: str, tone: Tone) -> DraftResponse:
    """Turn a workplace message + desired tone into a professional draft."""
    client = _get_client()

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=build_user_prompt(message, tone),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=DraftResponse,
        ),
    )

    draft: DraftResponse = response.parsed
    draft.tone = tone
    return draft
