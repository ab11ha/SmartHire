import streamlit as st
from app.matching.matcher import Matcher
from app.extractor.extract_text import extract_text_from_file

# Initialize matcher in session
if 'matcher' not in st.session_state:
    st.session_state.matcher = Matcher()

matcher = st.session_state.matcher

st.set_page_config(page_title="SmartHire Resume Matcher", layout="wide")
st.title("📄 SmartHire - Resume Matcher")

# Sidebar - Job Posting
with st.sidebar:
    st.header("📝 Post a Job")

    if "job_id" not in st.session_state:
        title = st.text_input("Job Title")
        location = st.text_input("Location")
        experience = st.text_input("Experience")
        skills = st.text_input("Skills (comma separated)")

        if st.button("Post Job"):
            if not (title and location and experience and skills):
                st.warning("⚠️ Please fill out all job fields.")
            else:
                job_meta = {
                    "title": title,
                    "location": location,
                    "experience": experience,
                    "skills": [s.strip() for s in skills.split(",")]
                }
                job_text = f"{title}. Skills: {skills}. Location: {location}. Experience: {experience}."
                job_id = matcher.add_job(job_text, job_meta)

                # Reset session state for new job
                st.session_state.job_id = job_id
                st.session_state.uploaded_applicants = 0
                st.session_state.registration_closed = False
                st.session_state.processed_files = set()  # ✅ clear processed files
                st.success(f"✅ Job posted successfully! Job ID: {job_id}")
    else:
        st.success("✅ Job already posted. You can now upload resumes.")

# Upload resumes section
if "job_id" in st.session_state and not st.session_state.get("registration_closed", False):
    st.subheader("📤 Upload Resumes")
    uploaded_files = st.file_uploader(
        "Upload at least 10 resumes", type=["pdf", "docx", "txt"], accept_multiple_files=True
    )

    if uploaded_files:
        for file in uploaded_files:
            if file.name in st.session_state.get("processed_files", set()):
                continue  # ✅ Skip duplicate resumes

            text = extract_text_from_file(file)
            if text:
                applicant_meta = {
                    "name": file.name.rsplit('.', 1)[0],
                    "email": f"{file.name.rsplit('.', 1)[0].replace(' ', '_')}@example.com",
                    "resume_text": text
                }
                matcher.add_applicant(text, applicant_meta, job_id=st.session_state.job_id)
                st.session_state.uploaded_applicants += 1
                st.session_state.processed_files.add(file.name)  # ✅ Track processed file
                st.success(f"✅ Processed: {file.name}")
            else:
                st.warning(f"⚠️ Could not extract text from {file.name}")

    st.markdown(f"**Uploaded Resumes:** `{st.session_state.uploaded_applicants}`")

# Close registration and rank applicants
if (
    "job_id" in st.session_state
    and st.session_state.uploaded_applicants >= 10
    and not st.session_state.get("registration_closed", False)
):
    st.info(f"✅ {st.session_state.uploaded_applicants} resumes uploaded.")
    if st.button("🔒 Close Registration & Rank Applicants"):
        st.session_state.registration_closed = True
        st.success("🔒 Registration closed. Ranking applicants...")
        if matcher.job_texts.get(st.session_state.job_id):
            rankings = matcher.graphrag_rank_applicants(st.session_state.job_id)
            st.session_state.rankings = rankings

# Display rankings
if st.session_state.get("registration_closed", False) and st.session_state.get("rankings"):
    st.subheader("📊 Top Matched Applicants")
    for i, (applicant_id, final_score, matched_keywords, sim_score) in enumerate(st.session_state.rankings, 1):
        applicant = matcher.db.get_applicant_by_id(applicant_id)
        st.markdown(f"### {i}. {applicant['name']}")
        st.markdown(f"📧 Email: {applicant['email']}")
        st.markdown(f"⭐ Final Score: `{final_score:.2f}`")
        st.markdown(f"🧠 Similarity: `{sim_score:.2f}`")
        st.markdown(f"🎯 Matched Skills: `{', '.join(matched_keywords) if matched_keywords else 'None'}`")
        st.markdown("---")

# Start new job session
if st.session_state.get("registration_closed"):
    if st.button("🔁 Start New Job Posting"):
        for key in ["job_id", "uploaded_applicants", "registration_closed", "rankings", "processed_files"]:
            st.session_state.pop(key, None)
        st.experimental_rerun()
