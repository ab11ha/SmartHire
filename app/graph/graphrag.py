import re
import networkx as nx

class GraphRAG:
    def __init__(self):
        self.graph = nx.Graph()

    def extract_experience_years(self, text):
        # Extended to support patterns like "5 years in Python" or "Python - 3 years"
        patterns = [
            r"(\d+\+?\s*(?:years?|yrs?).*?\b(?:in|of)?\s*(\w+))",
            r"(\w+).*?(\d+\+?\s*(?:years?|yrs?))"
        ]
        matches = []
        for pat in patterns:
            matches.extend(re.findall(pat, text, re.IGNORECASE))
        return matches

    def score_experience(self, text, skills):
        total_score = 0
        found = self.extract_experience_years(text)
        for entry in found:
            if isinstance(entry, tuple) and len(entry) >= 2:
                phrase = " ".join(entry).lower()
            else:
                phrase = entry.lower()
            for skill in skills:
                if skill.lower() in phrase:
                    y = re.search(r"(\d+)", phrase)
                    if y:
                        total_score += min(int(y.group(1)), 10) * 2.5
        return total_score

    def build_graph(self, job_meta, resume_text):
        self.graph.clear()
        job_node = "JOB"
        self.graph.add_node(job_node, type="job")
        for skill in job_meta.get("skills", []):
            self.graph.add_node(skill.lower(), type="skill")
            self.graph.add_edge(job_node, skill.lower())
        matches = [skill for skill in job_meta.get("skills", []) if skill.lower() in resume_text.lower()]
        return matches

    def get_graph_score(self, job_meta, resume_text):
        matched_skills = self.build_graph(job_meta, resume_text)
        experience_score = self.score_experience(resume_text, job_meta.get("skills", []))
        keyword_score = len(matched_skills) * 1.5
        multi_skill_bonus = 0
        if len(matched_skills) >= 2:
            multi_skill_bonus = 1.0 + (0.5 * (len(matched_skills) - 2))
        total_score = keyword_score + experience_score + multi_skill_bonus
        return matched_skills, total_score