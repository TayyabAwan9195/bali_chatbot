# ============================================================
# FILE: rag_engine.py
# PURPOSE: Groq API integration for RAG responses
# ============================================================

import logging
from typing import List, Optional
from groq import Groq
from core.config import (
    GROQ_API_KEY,
    GROQ_MODEL,
    GROQ_MAX_TOKENS,
    GROQ_TEMPERATURE,
    SYSTEM_PROMPT,
    MAX_HISTORY_MESSAGES
)

# --- Client setup ---
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


def _load_knowledge_base() -> str:
    import json
    from pathlib import Path

    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    knowledge = []

    # Load chunks
    try:
        chunks_file = PROJECT_ROOT / "data" / "chunks.json"
        if chunks_file.exists():
            data = json.loads(chunks_file.read_text(encoding="utf-8"))
            for chunk in data.get("chunks", [])[:15]:
                knowledge.append(str(chunk))
    except Exception as e:
        logging.warning(f"Could not load chunks: {e}")

    # Load FAQs
    try:
        faq_file = PROJECT_ROOT / "data" / "faq.json"
        if faq_file.exists():
            data = json.loads(faq_file.read_text(encoding="utf-8"))
            for faq in data.get("faq", [])[:25]:
                knowledge.append(
                    f"Q: {faq.get('question', '')}\n"
                    f"A: {faq.get('answer', '')}"
                )
    except Exception as e:
        logging.warning(f"Could not load FAQ: {e}")

    return "\n\n".join(knowledge)


# Load once at startup
_KNOWLEDGE_BASE = _load_knowledge_base()

# --- Main function ---
def generate_with_context(
    question: str,
    contexts: List[str],
    history: Optional[list] = None,
) -> str:
    full_context = "\n\n".join(contexts)

    # Build messages
    system_prompt = SYSTEM_PROMPT.replace("{knowledge_base}", _KNOWLEDGE_BASE)
    messages = [
        {
            "role": "system",
            "content": system_prompt,
        }
    ]

    recent_history = history[-MAX_HISTORY_MESSAGES:] if history else []
    for msg in recent_history:
        if isinstance(msg, dict) and "role" in msg and "content" in msg and msg["role"] in ["user", "assistant"]:
            messages.append({"role": msg["role"], "content": msg["content"]})

    # Add the user question with context as the last message
    messages.append(
        {
            "role": "user",
            "content": (
                f"Relevant context:\n{full_context}\n\n"
                f"User message: {question}"
            ),
        }
    )

    if client is None:
        return "I'm having technical difficulties, please try again shortly."

    try:
        resp = client.chat.completions.create(
            model=GROQ_MODEL,
            max_tokens=GROQ_MAX_TOKENS,
            temperature=GROQ_TEMPERATURE,
            messages=messages,
        )
        return resp.choices[0].message.content.strip()
    except Exception as exc:
        logging.exception("Groq request failed")
        return "I'm having technical difficulties, please try again shortly."