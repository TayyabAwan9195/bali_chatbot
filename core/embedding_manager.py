import os
import json
import numpy as np
import re
from sentence_transformers import SentenceTransformer
# from text_preprocessor import preprocess


def preprocess(text: str) -> str:
    """Preprocess text for embedding: lowercase, remove punctuation, strip."""
    if not text:
        return ""
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # Strip whitespace
    return text.strip()


class EmbeddingManager:
    def __init__(self,
                 faq_path: str = "data/faq.json",
                 emb_path: str = "cache/embeddings.npy",
                 model_name: str = "all-MiniLM-L6-v2"):
        self.faq_path = faq_path
        self.emb_path = emb_path
        self.model_name = model_name
        self.model = SentenceTransformer(self.model_name)
        self.faq_list = self._load_faq()
        # questions are preprocessed versions of FAQ questions + keywords
        self.questions = [
            preprocess(item.get("question", "") + " " + item.get("keywords", ""))
            for item in self.faq_list
        ]
        self.embeddings = self._load_or_create_embeddings()

        # load or compute text chunks from PDF for RAG
        self.chunks = self._load_chunks()
        self.chunk_embeddings = self._load_or_create_chunk_embeddings()

    def _load_faq(self):
        with open(self.faq_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("faq", [])

    def _load_or_create_embeddings(self):
        if os.path.exists(self.emb_path):
            try:
                arr = np.load(self.emb_path)
                # ensure correct dtype
                return arr.astype("float32")
            except Exception:
                # if load fails, rebuild
                pass
        # build embeddings from scratch
        emb = self.model.encode(self.questions, show_progress_bar=False)
        emb = np.array(emb).astype("float32")
        np.save(self.emb_path, emb)
        return emb

    def _load_chunks(self):
        # read chunks.json produced by parse_pdf
        if os.path.exists("data/chunks.json"):
            with open("data/chunks.json","r",encoding="utf-8") as f:
                data = json.load(f)
            return data.get("chunks", [])
        # if not available, ask parse_pdf to regenerate
        try:
            from parse_pdf import extract_text_chunks, PDF_PATH
            chunks = extract_text_chunks(PDF_PATH)
            with open("data/chunks.json","w",encoding="utf-8") as f:
                json.dump({"chunks": chunks}, f, indent=2, ensure_ascii=False)
            return chunks
        except Exception:
            return []

    def _load_or_create_chunk_embeddings(self):
        path = "cache/chunks_embeddings.npy"
        if os.path.exists(path):
            try:
                arr = np.load(path)
                return arr.astype("float32")
            except Exception:
                pass
        if self.chunks:
            emb = self.model.encode(self.chunks, show_progress_bar=False)
            emb = np.array(emb).astype("float32")
            np.save(path, emb)
            return emb
        return np.zeros((0, self.model.get_sentence_embedding_dimension()), dtype="float32")
