# ============================================================
# FILE: database.py
# PURPOSE: Database operations for user state management
# ============================================================

import json
import sqlite3
from datetime import datetime
from typing import Dict, Any
from core.config import DB_FILE, MAX_HISTORY_DB

class DBHelper:
    def __init__(self, db_file: str = DB_FILE):
        self.db_file = db_file
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database with the new leads table."""
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                user_id TEXT PRIMARY KEY,
                step TEXT DEFAULT 'start',
                pending_flow TEXT,
                lead_category TEXT,
                follow_up_sent BOOLEAN DEFAULT 0,
                last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                history TEXT DEFAULT '[]',  -- JSON array of last 10 messages
                lead_info TEXT DEFAULT '{}',  -- JSON object
                qualification TEXT DEFAULT '{}'  -- JSON object
            )
        """)
        self.conn.commit()

    def load_state(self, user_id: str) -> Dict[str, Any]:
        """Load user state from DB."""
        cursor = self.conn.execute(
            "SELECT step, pending_flow, lead_category, follow_up_sent, last_interaction, history, lead_info, qualification FROM leads WHERE user_id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        if row:
            step, pending_flow, lead_category, follow_up_sent, last_interaction, history, lead_info, qualification = row
            qual = json.loads(qualification) if qualification else {}
            return {
                "step": step or "start",
                "pending_flow": pending_flow,
                "lead_category": lead_category,
                "follow_up_sent": bool(follow_up_sent),
                "last_interaction": datetime.fromisoformat(last_interaction) if last_interaction else datetime.now(),
                "history": json.loads(history) if history else [],
                "lead_info": json.loads(lead_info) if lead_info else {},
                "qualification": qual,
                "last_question": qual.get("last_question", ""),
                "message_count": qual.get("message_count", 0),  # Store in qualification for persistence
                "last_minute": datetime.fromisoformat(qual["last_minute"]) if qual.get("last_minute") else None
            }
        else:
            # Default state
            return {
                "step": "start",
                "pending_flow": None,
                "lead_category": None,
                "follow_up_sent": False,
                "last_interaction": datetime.now(),
                "history": [],
                "lead_info": {},
                "qualification": {},
                "last_question": "",
                "message_count": 0,
                "last_minute": None
            }

    def save_state(self, user_id: str, **kwargs):
        """Save user state to DB. Accepts keyword arguments for fields to update."""
        # Load current state
        current = self.load_state(user_id)
        # Update with provided kwargs
        for key, value in kwargs.items():
            if key == "history" and isinstance(value, list):
                # Limit to last 10 messages
                value = value[-MAX_HISTORY_DB:]
            current[key] = value
        # Update qualification with last_question
        current["qualification"]["last_question"] = current.get("last_question", "")
        # Store rate limiting in qualification
        current["qualification"]["message_count"] = current.get("message_count", 0)
        last_min = current.get("last_minute")
        current["qualification"]["last_minute"] = last_min.isoformat() if last_min else None
        # Serialize JSON fields
        history_json = json.dumps(current["history"])
        lead_info_json = json.dumps(current["lead_info"])
        qualification_json = json.dumps(current["qualification"])
        # Insert or update
        self.conn.execute("""
            INSERT INTO leads (user_id, step, pending_flow, lead_category, follow_up_sent, last_interaction, history, lead_info, qualification)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                step=excluded.step,
                pending_flow=excluded.pending_flow,
                lead_category=excluded.lead_category,
                follow_up_sent=excluded.follow_up_sent,
                last_interaction=excluded.last_interaction,
                history=excluded.history,
                lead_info=excluded.lead_info,
                qualification=excluded.qualification
        """, (
            user_id,
            current["step"],
            current["pending_flow"],
            current["lead_category"],
            int(current["follow_up_sent"]),
            current["last_interaction"].isoformat(),
            history_json,
            lead_info_json,
            qualification_json
        ))
        self.conn.commit()