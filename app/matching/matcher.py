import numpy as np
from app.embeddings.embedder import Embedder
from app.embeddings.faiss_index import FaissIndex
from app.storage.sqlite_db import SQLiteDB as Database
from app.graph.graphrag import GraphRAG

class Matcher:
    def __init__(self):
        self.embedder = Embedder()
        self.index = FaissIndex(dimension=384)
        self.db = Database()
        self.rag = GraphRAG()
        self.applicant_texts = {}
        self.job_texts = {}
        self.job_applicants_map = {}

    def _validate_embedding(self, embedding, label="Embedding"):
        if embedding is None or not isinstance(embedding, np.ndarray):
            raise ValueError(f"{label} is not a valid numpy array.")
        if np.isnan(embedding).any() or np.isinf(embedding).any():
            raise ValueError(f"{label} contains NaN or Inf.")
        return embedding

    def add_job(self, jd_text, job_meta):
        jd_embedding = self._validate_embedding(self.embedder.get_embedding(jd_text), "Job embedding")
        job_id = self.db.insert_job(job_meta)
        self.index.add(jd_embedding, f"job_{job_id}")
        self.job_texts[job_id] = jd_text
        self.job_applicants_map[job_id] = []
        return job_id

    def add_applicant(self, resume_text, applicant_meta, job_id=None):
        resume_embedding = self._validate_embedding(self.embedder.get_embedding(resume_text), "Resume embedding")
        applicant_id = self.db.insert_applicant(applicant_meta)
        self.index.add(resume_embedding, f"applicant_{applicant_id}")
        self.applicant_texts[applicant_id] = resume_text
        if job_id is not None:
            self.job_applicants_map.setdefault(job_id, []).append(applicant_id)
        return applicant_id

    def get_applicant_text(self, applicant_id):
        return self.applicant_texts.get(applicant_id, "")

    def get_job_text(self, job_id):
        return self.job_texts.get(job_id, "")

    def graphrag_rank_applicants(self, job_id, top_k=10):
        job_text = self.get_job_text(job_id)
        job_meta = self.db.get_job_by_id(job_id)
        jd_embedding = self._validate_embedding(self.embedder.get_embedding(job_text), "Job embedding")
        scored_applicants = []

        for applicant_id in self.job_applicants_map.get(job_id, []):
            resume_text = self.get_applicant_text(applicant_id)
            if not resume_text:
                continue
            matched_keywords, graph_score = self.rag.get_graph_score(job_meta, resume_text)
            resume_embedding = self.embedder.get_embedding(resume_text)
            sim_score = float(np.dot(jd_embedding, resume_embedding))
            final_score = sim_score + graph_score
            scored_applicants.append((applicant_id, final_score, matched_keywords, sim_score))

        scored_applicants.sort(key=lambda x: x[1], reverse=True)
        return scored_applicants[:top_k]
    def clear_applicants_for_job(self, job_id):
        """
        Clears all applicants and embeddings related to a specific job ID.
        Useful when starting fresh for the same job or rerunning uploads.
        """
        applicant_ids = self.job_applicants_map.get(job_id, [])
        for applicant_id in applicant_ids:
            if applicant_id in self.applicant_texts:
                del self.applicant_texts[applicant_id]
        self.job_applicants_map[job_id] = []