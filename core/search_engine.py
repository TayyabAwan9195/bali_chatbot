import faiss
import numpy as np
import re
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


class SearchEngine:
    def __init__(self, embedding_manager, top_k: int = 5, threshold: float = 1.2):
        self.faq = embedding_manager.faq_list
        self.questions = embedding_manager.questions
        self.embeddings = embedding_manager.embeddings
        self.model = embedding_manager.model
        self.top_k = top_k
        self.threshold = threshold

        # FAQ index
        if self.embeddings.size > 0:
            dim = self.embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dim)
            self.index.add(self.embeddings)
        else:
            self.index = None
        self.answers = [item.get("answer", "") for item in self.faq]

        # chunks index for RAG
        self.chunks = getattr(embedding_manager, "chunks", [])
        self.chunk_index = None
        if hasattr(embedding_manager, "chunk_embeddings") and embedding_manager.chunk_embeddings.size > 0:
            dim2 = embedding_manager.chunk_embeddings.shape[1]
            self.chunk_index = faiss.IndexFlatL2(dim2)
            self.chunk_index.add(embedding_manager.chunk_embeddings)

    def retrieve_chunks(self, query_text: str, top_k: int = 3):
        """Return top_k relevant text chunks along with distances."""
        if self.chunk_index is None:
            return []
        q = preprocess(query_text)
        q_emb = self.model.encode([q])
        q_emb = np.array(q_emb).astype("float32")
        distances, indices = self.chunk_index.search(q_emb, top_k)
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.chunks):
                results.append((self.chunks[idx], dist))
        return results

    def query(self, query_text: str):
        q = preprocess(query_text)
        q_emb = self.model.encode([q])
        q_emb = np.array(q_emb).astype("float32")
        distances, indices = self.index.search(q_emb, self.top_k)
        # always return best match with its distance
        best_idx = indices[0][0]
        best_dist = distances[0][0]
        best_ans = self.answers[best_idx]
        # if within threshold consider confident
        if best_dist <= self.threshold:
            return best_ans, best_dist
        # otherwise return best answer and distance anyway for downstream handling
        return best_ans, best_dist

