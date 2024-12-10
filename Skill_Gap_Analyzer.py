import streamlit as st
import pdfplumber
from transformers import pipeline
from fuzzywuzzy import fuzz

# Define job roles and corresponding skill keywords
JOB_ROLES = {
    "Data Scientist": ["python", "machine learning", "deep learning", "sql", "statistics", "tensorflow", "scikit-learn"],
    "Web Developer": ["html", "css", "javascript", "react", "node.js"],
    "Cloud Engineer": ["aws", "azure", "kubernetes", "docker", "devops"],
}

# Set up Streamlit
st.set_page_config(page_title="Resume Analyzer", layout="wide")
st.title("📄 Resume Analyzer")

# Upload Resume
uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])

# Select Job Role
job_role = st.selectbox("Select a Job Role:", options=["Choose"] + list(JOB_ROLES.keys()))

# Analyze Button
if st.button("Analyze Resume"):
    if not uploaded_file or job_role == "Choose":
        st.error("Please upload a resume and select a job role!")
    else:
        # Step 1: Extract text from PDF
        with pdfplumber.open(uploaded_file) as pdf:
            resume_text = " ".join(page.extract_text() for page in pdf.pages if page.extract_text())
        
        # Normalize text for comparison
        resume_text = resume_text.lower()

        # Step 2: Check skills in the resume
        required_skills = [skill.lower() for skill in JOB_ROLES[job_role]]
        matched_skills = [
            skill for skill in required_skills
            if any(fuzz.partial_ratio(skill, word) > 85 for word in resume_text.split())
        ]
        
        # Step 3: Identify missing skills
        missing_skills = list(set(required_skills) - set(matched_skills))

        # Display results
        st.subheader("Skills Matched")
        st.write(matched_skills if matched_skills else "No matching skills found.")
        
        st.subheader("Missing Skills")
        st.write(missing_skills if missing_skills else "No missing skills!")

        # Step 4: Recommend related skills for missing ones
        if missing_skills:
            st.subheader("Skill Recommendations")
            for skill in missing_skills:
                st.write(f"- Related skills for **{skill}**: {skill}-specific tools or frameworks")

