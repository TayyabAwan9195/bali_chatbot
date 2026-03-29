# ============================================================
# FILE: flow_manager.py
# PURPOSE: Business flow management and lead qualification
# ============================================================

# FlowManager is kept as fallback only.
# Main conversation is handled by Groq (via core/rag_engine.py).

from typing import Dict, Any
from core.database import DBHelper
from core.validators import (
    validate_business_type,
    validate_start_date,
    validate_shareholders,
    validate_company_status,
    is_meaningless_message
)
from core.config import MENU_MESSAGE

class FlowManager:
    def __init__(self, db_helper: DBHelper):
        self.db = db_helper

    def update_history(self, user_id: str, role: str, content: str):
        """Update conversation history."""
        state = self.db.load_state(user_id)
        history = state["history"]
        history.append({"role": role, "content": content})
        self.db.save_state(user_id, history=history)

    def update_lead_info(self, user_id: str, **info):
        """Update lead_info."""
        state = self.db.load_state(user_id)
        lead_info = state["lead_info"]
        lead_info.update(info)
        self.db.save_state(user_id, lead_info=lead_info)

    def update_qualification(self, user_id: str, **qual):
        """Update qualification."""
        state = self.db.load_state(user_id)
        qualification = state["qualification"]
        qualification.update(qual)
        # Update lead category based on qualification
        lead_cat = self._categorize_lead(qualification)
        self.db.save_state(user_id, qualification=qualification, lead_category=lead_cat)

    def _categorize_lead(self, qualification: Dict[str, Any]) -> str:
        """Advanced lead tagging with reasoning."""
        start_time = qualification.get("start_date", "").lower()
        budget_ok = qualification.get("budget_ok")
        biz_type = qualification.get("biz_type", "").lower()

        # Reasoning logic
        if budget_ok is False:
            return "COLD_LEAD"  # Budget not OK
        if any(word in start_time for word in ["1 month", "2 months", "3 months", "soon", "immediately"]):
            if budget_ok is True and biz_type:
                return "HOT_LEAD"  # Ready soon, budget OK, business specified
            return "WARM_LEAD"  # Ready soon but missing details
        elif any(word in start_time for word in ["later", "few months", "year", "interested"]):
            if budget_ok is True:
                return "WARM_LEAD"  # Interested, budget OK
            return "COLD_LEAD"  # Interested but budget issue
        return "COLD_LEAD"  # Default

    def handle_company_setup_flow(self, user_id: str, message: str) -> str:
        """Company setup flow with qualification."""
        state = self.db.load_state(user_id)
        step = state.get("step", "start")
        qual = state["qualification"]

        if step == "company_setup_info":
            response = (
                "Company Setup (PT PMA) at Bali Legal Partner:\n"
                "• Cost: IDR 30,000,000\n"
                "• Processing time: 5 working days\n"
                "• Requirements: Two shareholders, passport copies, business activity description\n\n"
                "What type of business are you planning to start?"
            )
            self.db.save_state(user_id, step="qual_biz_type", last_question=response)
            return response

        if step == "qual_biz_type":
            if not validate_business_type(message.strip()):
                last_q = state.get("last_question", "What type of business are you planning to start?")
                return f"I'm sorry, that doesn't seem like a valid business type. {last_q}"
            qual["biz_type"] = message.strip()
            self.update_qualification(user_id, biz_type=message.strip())
            response = "When are you planning to start operations? (e.g., within 1 month, 3 months, etc.)"
            self.db.save_state(user_id, step="qual_start_date", last_question=response)
            return response

        if step == "qual_start_date":
            if not validate_start_date(message.strip()):
                last_q = state.get("last_question", "When are you planning to start operations? (e.g., within 1 month, 3 months, etc.)")
                return f"I'm sorry, that doesn't seem like a valid timeframe. {last_q}"
            qual["start_date"] = message.strip()
            self.update_qualification(user_id, start_date=message.strip())
            response = (
                "Thanks. For transparency, the company setup fee is IDR 30,000,000 and ongoing compliance starts from IDR 2,000,000 per month.\n"
                "Is this within your current budget to proceed? (Yes / No)"
            )
            self.db.save_state(user_id, step="qual_budget", last_question=response)
            return response

        if step == "qual_budget":
            lower = message.strip().lower()
            if any(x in lower for x in ["yes", "y", "ok", "sure", "sounds good", "within budget"]):
                qual["budget_ok"] = True
            elif any(x in lower for x in ["no", "not", "can't", "cannot", "too", "outside"]):
                qual["budget_ok"] = False
            else:
                last_q = state.get("last_question", "Is this within your current budget to proceed? (Yes / No)")
                return f"Please answer with Yes or No. {last_q}"
            self.update_qualification(user_id, budget_ok=qual["budget_ok"], budget_text=qual.get("budget_text"))
            response = "Great. How many shareholders will the company have?"
            self.db.save_state(user_id, step="qual_shareholders", last_question=response)
            return response

        if step == "qual_shareholders":
            if not validate_shareholders(message.strip()):
                last_q = state.get("last_question", "Great. How many shareholders will the company have?")
                return f"I'm sorry, that doesn't seem like a valid number of shareholders. {last_q}"
            qual["shareholders"] = message.strip()
            self.update_qualification(user_id, shareholders=message.strip())
            # Handover
            lead_cat = state["lead_category"]
            handover = (
                "Thank you for your information. One of our legal advisors from Bali Legal Partner will contact you shortly.\n\n"
                f"{self._upsell_after_company()}\n\n"
                f"{self._generate_sales_prompt(lead_cat)}"
            )
            self.db.save_state(user_id, step="completed")
            return handover

        return "Please provide more details so I can assist you."

    def handle_visa_flow(self, user_id: str, message: str) -> str:
        """Investor visa flow."""
        state = self.db.load_state(user_id)
        step = state.get("step", "start")
        qual = state["qualification"]

        if step == "visa_info":
            response = (
                "Investor Visa (KITAS) at Bali Legal Partner:\n"
                "• Cost: IDR 18,500,000 per person\n"
                "• Processing time: 5-7 working days after company setup\n"
                "• Requirements: Passport, photo, CV, bank statement (min USD 2,000)\n\n"
                "Do you already have a company in Indonesia, or do you need help setting one up?"
            )
            self.db.save_state(user_id, step="visa_company_status", last_question=response)
            return response

        if step == "visa_company_status":
            if not validate_company_status(message.strip()):
                last_q = state.get("last_question", "Do you already have a company in Indonesia, or do you need help setting one up?")
                return f"I'm sorry, that doesn't seem like a valid response. {last_q}"
            qual["company_status"] = message.strip()
            self.update_qualification(user_id, company_status=message.strip())
            response = "When would you like to apply for the visa?"
            self.db.save_state(user_id, step="visa_start_date", last_question=response)
            return response

        if step == "visa_start_date":
            if not validate_start_date(message.strip()):
                last_q = state.get("last_question", "When would you like to apply for the visa?")
                return f"I'm sorry, that doesn't seem like a valid timeframe. {last_q}"
            qual["start_date"] = message.strip()
            self.update_qualification(user_id, start_date=message.strip())
            # Handover
            lead_cat = state["lead_category"]
            handover = (
                "Thanks! One of our legal advisors from Bali Legal Partner will reach out soon to guide you through the investor visa process.\n\n"
                f"{self._upsell_after_company()}\n\n"
                f"{self._generate_sales_prompt(lead_cat)}"
            )
            self.db.save_state(user_id, step="completed")
            return handover

        return "Could you share a bit more so I can assist you with the visa process?"

    def handle_business_license_flow(self, user_id: str, message: str) -> str:
        """Business licensing flow."""
        state = self.db.load_state(user_id)
        step = state.get("step", "start")

        if step == "license_info":
            response = (
                "Bali Legal Partner can help you with business licensing (including villa/Airbnb, KBLI, and other permits).\n"
                "Please tell me what type of license or business activity you need."
            )
            self.db.save_state(user_id, step="license_activity", last_question=response)
            return response

        if step == "license_activity":
            if not message.strip() or is_meaningless_message(message):
                last_q = state.get("last_question", "Please tell me what type of license or business activity you need.")
                return f"I'm sorry, that doesn't seem like a valid license type. {last_q}"
            self.update_qualification(user_id, license_activity=message.strip())
            self.db.save_state(user_id, step="completed")
            return (
                "Thank you. One of our licensing specialists will review your request and contact you shortly.\n"
                "You can also share photos or documents if you have them.\n\n"
                f"{self._upsell_after_company()}"
            )

        return "Please tell me more about the license or permit you need."

    def handle_tax_accounting_flow(self, user_id: str, message: str) -> str:
        """Tax and accounting flow."""
        state = self.db.load_state(user_id)
        step = state.get("step", "start")

        if step == "tax_info":
            response = (
                "We provide tax and accounting services for PMA companies in Indonesia, including monthly reporting, payroll, and LKPM.\n"
                "What type of tax/accounting support are you looking for?"
            )
            self.db.save_state(user_id, step="tax_needs", last_question=response)
            return response

        if step == "tax_needs":
            if not message.strip() or is_meaningless_message(message):
                last_q = state.get("last_question", "What type of tax/accounting support are you looking for?")
                return f"I'm sorry, that doesn't seem like a valid tax/accounting need. {last_q}"
            self.update_qualification(user_id, tax_needs=message.strip())
            self.db.save_state(user_id, step="completed")
            return (
                "Thanks! A member of our accounting team will reach out to discuss your needs and provide a tailored quote.\n\n"
                f"{self._upsell_after_company()}"
            )

        return "Could you describe what kind of tax or accounting support you need?"

    def _upsell_after_company(self) -> str:
        return (
            "While we help with company setup, we can also assist with:\n"
            "• Investor visa applications\n"
            "• Bank account opening\n"
            "• Accounting and tax services\n"
            "• Business licensing (KBLI / villa / Airbnb)"
        )

    def _generate_sales_prompt(self, lead_category: str) -> str:
        """Generate sales closing prompts."""
        if lead_category == "HOT_LEAD":
            return "If you send the passport copies today, we can begin the registration immediately."
        elif lead_category == "WARM_LEAD":
            return "Would you like us to check the available company name for you?"
        else:
            return (
                "If you are ready to proceed, please send:\n"
                "• Passport copies of two shareholders\n"
                "• Three preferred company names\n"
                "• Description of your business activity"
            )