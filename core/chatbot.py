# ============================================================
# FILE: chatbot.py
# PURPOSE: Main chatbot logic and response handling
# ============================================================

import logging
import re
from typing import Optional
from datetime import datetime, timedelta
from core.config import (
    FAQ_CONFIDENCE_THRESHOLD,
    RAG_CONFIDENCE_THRESHOLD,
    RAG_TOP_K,
    MAX_MESSAGES_PER_MINUTE,
    MENU_MESSAGE
)
from core.validators import is_meaningless_message, is_question
from core.database import DBHelper
from core.flow_manager import FlowManager
from core.rag_engine import generate_with_context
from core.embedding_manager import EmbeddingManager
from core.search_engine import SearchEngine

class Chatbot:
    def __init__(self):
        self.db_helper = DBHelper()
        self.flow_manager = FlowManager(self.db_helper)
        self.embed_mgr = EmbeddingManager()
        self.search_engine = SearchEngine(self.embed_mgr)
        self.logger = self._configure_logger()

    def _configure_logger(self):
        logger = logging.getLogger("chatbot")
        logger.setLevel(logging.INFO)
        fh = logging.FileHandler("chatbot.log", encoding="utf-8")
        fmt = logging.Formatter("%(asctime)s - %(message)s")
        fh.setFormatter(fmt)
        if not logger.handlers:
            logger.addHandler(fh)
        return logger

    def log_interaction(self, user_id: str, question: str, path: str, answer: str, score: Optional[float] = None):
        """Log each interaction."""
        self.logger.info(f"user_id={user_id} question={question} path={path} score={score} answer={answer}")

    def detect_intent(self, text: str) -> str:
        """Detect user intent using simple keyword matching."""
        t = text.lower().strip()

        # PROBLEM 2 FIX: Add greeting detection at the very top
        greeting_words = ["hi", "hello", "hey", "how are you", "what is your name", "who are you", "good morning", "good evening"]
        if any(g in t for g in greeting_words):
            return "greeting"

        def token_match(token: str) -> bool:
            return re.search(rf"\b{re.escape(token)}\b", t) is not None

        if any(word in t for word in ["price", "cost", "fee", "much", "how much"]):
            return "pricing"
        if any(word in t for word in ["how long", "duration", "time", "days", "timeline"]):
            return "timeline"
        if any(word in t for word in ["what do you need", "documents", "requirements"]):
            return "requirements"
        if any(word in t for word in ["restricted", "not allowed", "cannot"]):
            return "restricted_businesses"
        if any(word in t for word in ["start", "begin", "proceed", "i want to start", "lets start", "let's start"]):
            return "start_process"
        if any(token_match(word) for word in ["company", "set up", "register", "pma", "open a company"]):
            return "company_setup"
        if t.strip() in ["1", "1️⃣"]:
            return "company_setup"
        if any(token_match(word) for word in ["visa", "investor visa", "kitas"]):
            return "investor_visa"
        if t.strip() in ["2", "2️⃣"]:
            return "investor_visa"
        if any(token_match(word) for word in ["license", "licensing", "business license", "kbli"]):
            return "business_licensing"
        if t.strip() in ["3", "3️⃣"]:
            return "business_licensing"
        if any(token_match(word) for word in ["tax", "accounting"]):
            return "tax_accounting"
        if t.strip() in ["4", "4️⃣"]:
            return "tax_accounting"
        if t.strip() == "5":
            return "show_menu"
        if any(word in t for word in ["airbnb", "villa"]):
            return "business_licensing"
        return "general"

    def _collect_lead_info(self, user_id: str, message: str) -> Optional[str]:
        """Collect basic lead info."""
        state = self.db_helper.load_state(user_id)
        lead = state["lead_info"]
        step = state.get("step")

        if step == "collect_name":
            name = message.strip().capitalize()
            self.flow_manager.update_lead_info(user_id, name=name)
            self.db_helper.save_state(user_id, step="collect_country")
            return "Thanks! Which country are you currently based in?"

        if step == "collect_country":
            self.flow_manager.update_lead_info(user_id, country=message.strip())
            self.db_helper.save_state(user_id, step="collect_business_type")
            return "Great. What type of business are you planning to run?"

        if step == "collect_business_type":
            self.flow_manager.update_lead_info(user_id, business_type=message.strip())
            # Return to pending flow
            pending = state.get("pending_flow", "start")
            self.db_helper.save_state(user_id, step=pending)
            return None

        # If missing, start collection
        if not lead.get("name"):
            self.db_helper.save_state(user_id, step="collect_name", pending_flow=state.get("step", "start"))
            return "To help you better, may I have your name?"
        if not lead.get("country"):
            self.db_helper.save_state(user_id, step="collect_country", pending_flow=state.get("step", "start"))
            return "Which country are you currently based in?"
        if not lead.get("business_type"):
            self.db_helper.save_state(user_id, step="collect_business_type", pending_flow=state.get("step", "start"))
            return "What type of business are you planning to run?"
        return None

    def _get_rag_response(self, message: str, history: list) -> tuple:
        try:
            answer, dist = self.search_engine.query(message)
            if answer and dist and dist < RAG_CONFIDENCE_THRESHOLD:
                return answer, dist
            chunks = self.search_engine.retrieve_chunks(message, top_k=RAG_TOP_K)
            if chunks:
                context_texts = [c for c, _ in chunks]
                response = generate_with_context(message, context_texts, history=history)
                return response, None
            return (
                "I specialize in PT PMA company setup, investor visas, and business services in Indonesia. How can I help you?", None
            )
        except Exception:
            self.logger.exception("RAG error")
            return (
                "I'm experiencing technical difficulties. Please try again later.", None
            )

    def get_response(self, user_id: str, message: str) -> str:
        """Central response method."""
        # PROBLEM 3 FIX: Initialize dist and answer at top
        dist = None
        answer = None

        state = self.db_helper.load_state(user_id)

        # PROBLEM 4 FIX: Rate limiting
        current_minute = datetime.now().replace(second=0, microsecond=0)
        last_minute = state.get("last_minute")
        message_count = state.get("message_count", 0)
        if last_minute == current_minute:
            message_count += 1
        else:
            message_count = 1
            last_minute = current_minute
        if message_count > MAX_MESSAGES_PER_MINUTE:
            return "Please slow down. Try again in a moment."
        state["message_count"] = message_count
        state["last_minute"] = last_minute

        # Follow-up check
        if (datetime.now() - state["last_interaction"]) > timedelta(days=1) and not state["follow_up_sent"]:
            state["follow_up_sent"] = True
            follow_up_msg = (
                "Hello again 👋\n"
                "Just checking if you still need assistance with starting a company or investor visa in Indonesia.\n"
                "Our team at Bali Legal Partner would be happy to help."
            )
            self.flow_manager.update_history(user_id, "assistant", follow_up_msg)
            self.db_helper.save_state(user_id, follow_up_sent=True, last_interaction=datetime.now(), message_count=message_count, last_minute=last_minute)
            return follow_up_msg

        state["last_interaction"] = datetime.now()

        # Reset completed flows
        if state.get("step") == "completed":
            state["step"] = "start"
            # PROBLEM 5 FIX: Clear qualification but keep lead_info
            state["qualification"] = {}
            state["last_question"] = ""

        # First message greeting
        if len(state["history"]) == 0:
            greeting_msg = MENU_MESSAGE
            self.flow_manager.update_history(user_id, "assistant", greeting_msg)
            self.db_helper.save_state(user_id, last_interaction=datetime.now(), message_count=message_count, last_minute=last_minute)
            return greeting_msg

        # Record user message
        self.flow_manager.update_history(user_id, "user", message)

        # PROBLEM 1 FIX: At the TOP, before any flow handling, run FAQ search first if question
        if is_question(message):
            try:
                answer, dist = self.search_engine.query(message)
                if dist < FAQ_CONFIDENCE_THRESHOLD:
                    response = answer
                    self.flow_manager.update_history(user_id, "assistant", response)
                    self.log_interaction(user_id, message, "faq_direct", response, dist)
                    self.db_helper.save_state(user_id, last_interaction=datetime.now(), message_count=message_count, last_minute=last_minute)
                    return response
            except Exception:
                self.logger.exception("FAQ search error")

        # Check for meaningless messages
        if is_meaningless_message(message):
            last_q = state.get("last_question", "")
            if last_q:
                response = f"I'm sorry, I didn't understand that. {last_q}"
            else:
                response = "I'm sorry, I didn't understand that. How can I help you with company setup, visas, or business services?"
            self.flow_manager.update_history(user_id, "assistant", response)
            self.db_helper.save_state(user_id, last_interaction=datetime.now())
            return response

        # Check for real questions during flows (flow interruption)
        current_step = state.get("step", "start")
        if current_step not in ["start", "completed"] and is_question(message):
            response, dist = self._get_rag_response(message, state["history"])
            # Update history and return, without advancing flow
            self.flow_manager.update_history(user_id, "assistant", response)
            self.log_interaction(user_id, message, "rag_during_flow", response, dist if dist else None)
            self.db_helper.save_state(user_id, last_interaction=datetime.now(), message_count=message_count, last_minute=last_minute)
            return response

        # Detect intent
        intent = self.detect_intent(message)

        # Lead info collection
        if state.get("step") == "start":
            lead_prompt = self._collect_lead_info(user_id, message)
            if lead_prompt:
                self.flow_manager.update_history(user_id, "assistant", lead_prompt)
                return lead_prompt

        # Smart triggers
        if intent == "pricing":
            response = "Company Setup: IDR 30,000,000\nInvestor Visa: IDR 18,500,000\nCombined: IDR 48,500,000"
        elif intent == "timeline":
            response = "Company Setup: 5 working days\nInvestor Visa: 5-7 working days"
        elif intent == "requirements":
            response = (
                "For company setup: Passport copies of two shareholders, proposed company name, business description.\n"
                "For investor visa: Passport, photo, CV, bank statement (min USD 2,000)."
            )
        elif intent == "start_process":
            response = (
                "Great! Please send:\n"
                "• Passport copies of two shareholders\n"
                "• Three preferred company names\n"
                "• Description of your business activity"
            )
        elif intent == "greeting":
            response = MENU_MESSAGE
        elif intent == "company_setup":
            self.db_helper.save_state(user_id, step="company_setup_info")
            response = self.flow_manager.handle_company_setup_flow(user_id, message)
        elif intent == "investor_visa":
            self.db_helper.save_state(user_id, step="visa_info")
            response = self.flow_manager.handle_visa_flow(user_id, message)
        elif intent == "business_licensing":
            self.db_helper.save_state(user_id, step="license_info")
            response = self.flow_manager.handle_business_license_flow(user_id, message)
        elif intent == "tax_accounting":
            self.db_helper.save_state(user_id, step="tax_info")
            response = self.flow_manager.handle_tax_accounting_flow(user_id, message)
        elif intent == "show_menu":
            response = MENU_MESSAGE
        else:
            # RAG fallback for general and restricted_businesses intents
            response, dist = self._get_rag_response(message, state["history"])

        # Update history and log
        self.flow_manager.update_history(user_id, "assistant", response)
        self.log_interaction(user_id, message, intent, response, dist if dist else None)
        self.db_helper.save_state(user_id, last_interaction=datetime.now(), message_count=message_count, last_minute=last_minute)
        return response

# Entry point
bot = Chatbot()
