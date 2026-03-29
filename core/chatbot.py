# ============================================================
# FILE: chatbot.py
# PURPOSE: Main chatbot logic and response handling
# ============================================================

import logging
from datetime import datetime
from core.config import RAG_TOP_K, MAX_MESSAGES_PER_MINUTE
from core.database import DBHelper
from core.rag_engine import generate_with_context
from core.embedding_manager import EmbeddingManager
from core.search_engine import SearchEngine


class Chatbot:
    def __init__(self):
        self.db_helper = DBHelper()
        self.embed_mgr = EmbeddingManager()
        self.search_engine = SearchEngine(self.embed_mgr)
        self.logger = self._configure_logger()

    def _configure_logger(self):
        logger = logging.getLogger("chatbot")
        logger.setLevel(logging.INFO)
        from pathlib import Path

        LOG_DIR = Path(__file__).parent.parent / "logs"
        LOG_DIR.mkdir(exist_ok=True)
        fh = logging.FileHandler(LOG_DIR / "chatbot.log", encoding="utf-8")
        fmt = logging.Formatter("%(asctime)s - %(message)s")
        fh.setFormatter(fmt)
        if not logger.handlers:
            logger.addHandler(fh)
        return logger

    def log_interaction(self, user_id: str, question: str, path: str, answer: str, score: float | None = None):
        """Log each interaction."""
        self.logger.info(f"user_id={user_id} question={question} path={path} score={score} answer={answer}")

    def get_response(self, user_id: str, message: str) -> str:
        """Return assistant response by sending everything to Groq."""
        state = self.db_helper.load_state(user_id)

        # Rate limiting (per minute)
        current_minute = datetime.now().replace(second=0, microsecond=0)
        last_minute = state.get("last_minute")
        message_count = state.get("message_count", 0)
        if last_minute == current_minute:
            message_count += 1
        else:
            message_count = 1
            last_minute = current_minute

        if message_count > MAX_MESSAGES_PER_MINUTE:
            self.db_helper.save_state(
                user_id,
                message_count=message_count,
                last_minute=last_minute,
            )
            return "Please slow down. Try again in a moment."

        # Record user message in history (for context)
        self.db_helper.save_state(
            user_id,
            history=[*state.get("history", []), {"role": "user", "content": message}],
        )

        # Find relevant context via FAISS
        context_texts = []
        try:
            chunks = self.search_engine.retrieve_chunks(message, top_k=RAG_TOP_K)
            if chunks:
                context_texts = [c for c, _ in chunks]
        except Exception:
            self.logger.exception("FAISS search error")

        # Ask Groq for the response
        history = self.db_helper.load_state(user_id)["history"]
        raw_response = generate_with_context(message, context_texts, history=history)

        response = raw_response
        lead_category = None

        # Extract lead category tag (if present)
        if "LEAD_CATEGORY:" in raw_response:
            parts = raw_response.split("LEAD_CATEGORY:")
            response = parts[0].strip()
            cat = parts[1].strip().upper()
            if "HOT" in cat:
                lead_category = "HOT_LEAD"
            elif "WARM" in cat:
                lead_category = "WARM_LEAD"
            elif "COLD" in cat:
                lead_category = "COLD_LEAD"

        if lead_category:
            self.db_helper.save_state(user_id, lead_category=lead_category)
            self.logger.info(f"Lead {user_id} → {lead_category}")

        # Save assistant response and update state
        self.db_helper.save_state(
            user_id,
            history=[*self.db_helper.load_state(user_id)["history"], {"role": "assistant", "content": response}],
            last_interaction=datetime.now(),
            message_count=message_count,
            last_minute=last_minute,
        )

        self.log_interaction(user_id, message, "groq", response, None)
        return response


# Entry point
bot = Chatbot()
