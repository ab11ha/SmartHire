import faiss
import numpy as np

class FaissIndex:
    def __init__(self, dimension=384):  # fixed from 768 to 384
        self.index = faiss.IndexFlatIP(dimension)
        self.ids = []

    def add(self, embedding, id_):
        embedding = np.array(embedding, dtype=np.float32)
        self.index.add(np.array([embedding]))
        self.ids.append(id_)

    def search(self, query_embedding, top_k=5):
        if self.index.ntotal == 0:
            return []
        query_embedding = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
        distances, indices = self.index.search(query_embedding, top_k)
        results = []
        for rank, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.ids):
                results.append((self.ids[idx], float(distances[0][rank])))
        return results
    def reset(self):
        """Clears all embeddings and IDs – use when starting a new job posting."""
        self.index.reset()
        self.ids = []