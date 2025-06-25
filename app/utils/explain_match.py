import re

def explain_match(job_meta, resume_text):
    matched = []

    # Normalize resume text for matching
    resume_text = resume_text.lower()

    # Match skills
    for skill in job_meta.get("skills", []):
        skill_lower = skill.lower()
        if re.search(r'\b' + re.escape(skill_lower) + r'\b', resume_text):
            matched.append(skill)

    # Match location
    location = job_meta.get("location", "").lower()
    if location and location in resume_text:
        matched.append(job_meta["location"])  # Preserve original casing

    # Match experience (exact phrase)
    experience = job_meta.get("experience", "").lower()
    if experience and experience in resume_text:
        matched.append(job_meta["experience"])

    return matched
