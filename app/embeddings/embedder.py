from sentence_transformers import SentenceTransformer
import numpy as np

class Embedder:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def get_embedding(self, text):
        if not text or not isinstance(text, str):
            raise ValueError("Input must be a non-empty string.")
        embedding = self.model.encode(text, normalize_embeddings=True)
        return np.array(embedding, dtype=np.float32)

    def get_embeddings(self, texts):
        if not texts or not isinstance(texts, list):
            raise ValueError("Input must be a non-empty list of strings.")
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return np.array(embeddings, dtype=np.float32)