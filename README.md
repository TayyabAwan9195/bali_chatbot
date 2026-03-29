# Bali Chatbot

This repository contains a WhatsApp FAQ chatbot built with Flask, Twilio, SentenceTransformers, and FAISS. It answers questions about company setup, visas, licensing, and other legal services for foreigners in Indonesia.

## Project Structure

```
bali_chatbot/
├── core/                    # Core application modules
│   ├── __init__.py
│   ├── chatbot.py          # Main chatbot logic
│   ├── config.py           # Configuration constants
│   ├── database.py         # Database operations
│   ├── embedding_manager.py # Embedding management
│   ├── flow_manager.py     # Business flow management
│   ├── rag_engine.py       # Groq API integration
│   ├── search_engine.py    # FAISS search engine
│   └── validators.py       # Input validation functions
├── data/                   # Data files
│   ├── faq.json           # Extracted FAQs
│   ├── chunks.json        # PDF text chunks for RAG
│   └── AI_Chat_Bot_1.pdf  # Source PDF document
├── cache/                  # Cached embeddings and indexes
│   ├── embeddings.npy     # FAQ embeddings
│   └── chunks_embeddings.npy # PDF chunk embeddings
├── logs/                   # Log files
│   └── chatbot.log        # Application logs
├── dashboard/              # Dashboard templates (future)
├── static/                 # Static assets (CSS, JS)
├── templates/              # Flask templates
│   ├── admin_dashboard.html
│   ├── lead_detail.html
│   └── test_chat.html
├── app.py                  # Flask application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Features

* Extracts FAQs from PDF and maintains `data/faq.json`.
* **RAG support:** splits PDF into overlapping text chunks, embeds them, and retrieves relevant passages.
* Preprocesses text (lowercase, punctuation removal, synonyms).
* Creates/loads sentence embeddings (`cache/embeddings.npy` for FAQs, `cache/chunks_embeddings.npy` for PDF chunks) using `all-MiniLM-L6-v2`.
* FAISS indexes for fast similarity search of both FAQs and chunks.
* Combines retrieved context with user questions and sends to an LLM (Groq by default) for a generative answer.
* Qualification flow with sales prompts.
* Logging of every interaction (`logs/chatbot.log`).
* Web UI for live chat (`/chat`) with history.
* Flask webhook for Twilio WhatsApp (`/whatsapp`).
* Graceful fallback and domain-specific guidance.
* Simple production improvements (error handlers, debug off).

## Setup

1. **Clone the repository and navigate to the project directory**:
   ```bash
   git clone <repository-url>
   cd bali_chatbot
   ```

2. **Create & activate virtual environment** (Windows shown):
   ```powershell
   python -m venv venv
   & "venv\Scripts\Activate.ps1"
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```powershell
   cp .env.example .env
   # Edit .env and add your GROQ_API_KEY
   ```

5. **Extract FAQs from PDF** (run once, or when PDF changes):
   ```powershell
   python parse_pdf.py
   ```
   This appends new Q&A to `data/faq.json`, generating keywords automatically.

6. **Start the server**:
   ```powershell
   python app.py
   ```
   The service listens on `http://127.0.0.1:5000`.

## Using the UI

Open your browser and navigate to:

```
http://localhost:5000/
```
Click the link to `/chat` or go directly to `/chat`. Type questions in the box; answers and conversation history appear below.

## RAG and LLM setup

The bot now performs retrieval-augmented generation against the PDF content. Before using this feature you must set an environment variable with an API key for your chosen LLM provider (or hardcode it for local tests as shown in `rag_engine.py`). The default implementation now uses Google Gemini:

```powershell
setx GEMINI_API_KEY "your_key_here"
```

(Use `export` on macOS/Linux.) The code uses the `google-genai` package to call Gemini (previously `google-generativeai`); the dependency in `requirements.txt` has been updated accordingly. You can adapt `rag_engine.py` if you wish to swap providers or models.
## WhatsApp Integration

Configure Twilio to POST incoming messages to `https://<your-host>/whatsapp`. The same domain serves both the UI and the webhook. The bot replies using TwiML.

## Production Notes

* The Flask app runs with `debug=False` and handles exceptions gracefully.
* `logs/chatbot.log` records timestamped interactions and errors.
* The search engine returns the closest match even if confidence is low; the bot suggests possible answers and prompts for rephrasing.
* Unrelated questions yield a polite domain-specific guidance message.
* For deployment, consider using WSGI servers like Gunicorn or uWSGI, containerization, HTTPS, and rate limiting.

## Extending

* Add more synonyms in `text_preprocessor.py`.
* Expand `faq.json` manually or re-run `parse_pdf.py`.
* Customize UI by editing `app.py` or replacing with a React/Vue frontend.
* Implement multi-language translation or fuzzy matching if needed.

---

Deliver this folder to your client. They can run the service locally or deploy it to a cloud provider. All code is modular and production-ready for the specified FAQ domain.