import streamlit as st
from transformers import pipeline
import pdfplumber

# Predefined skills for job roles
JOB_ROLES = {
    "Data Scientist": ["Python", "R", "Machine Learning", "Deep Learning", "Natural Language Processing", "SQL", "Statistics"],
    "Machine Learning Engineer": ["Python", "Machine Learning", "Deep Learning", "Natural Language Processing", "TensorFlow", "PyTorch"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "React", "Node.js"],
    "Cloud Engineer": ["AWS", "Azure", "Kubernetes", "Docker", "DevOps"],
}

# Streamlit app setup
st.set_page_config(page_title="Resume Analyzer", layout="wide")
st.title(" Resume Analyzer")

# Upload resume
uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"], key="resume")

# Select job role
job_role = st.selectbox("Select a Job Role:", options=["Choose"] + list(JOB_ROLES.keys()))

# Analyze button
if st.button("Analyze Resume"):
    if not uploaded_file or job_role == "Choose":
        st.error("Please upload a resume and select a job role!")
    else:
        # Step 1: Extract text from PDF using pdfplumber
        with pdfplumber.open(uploaded_file) as pdf:
            resume_text = " ".join(page.extract_text() for page in pdf.pages if page.extract_text())
        
        # Step 2: Use transformers pipeline for content extraction
        skill_extractor = pipeline("feature-extraction")  # Use for extracting features from text
        extracted_features = skill_extractor(resume_text)

        # Step 3: Match skills based on keywords
        required_skills = JOB_ROLES[job_role]
        matched_skills = [skill for skill in required_skills if skill.lower() in resume_text.lower()]
        missing_skills = list(set(required_skills) - set(matched_skills))

        # Display results
        st.write("### Skills Matched:")
        st.write(matched_skills if matched_skills else "No skills matched.")

        st.write("### Missing Skills:")
        st.write(missing_skills if missing_skills else "No missing skills. Great job!")

        # Optional: Suggest missing skills
        if missing_skills:
            st.write("### Recommended Skills for Improvement:")
            for skill in missing_skills:
                st.write(f"- {skill}: Improve your knowledge and practical applications in {skill}.")
