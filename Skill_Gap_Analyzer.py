import streamlit as st
import PyPDF2
import spacy
from sentence_transformers import SentenceTransformer, util
import os
import subprocess

# Check if spaCy model is installed, and download if not
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    with st.spinner("Downloading spaCy language model..."):
        subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
    nlp = spacy.load("en_core_web_sm")

# Load the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Predefined skills for job roles
job_skills = {
    "Data Scientist": ["python", "machine learning", "data analysis", "sql", "deep learning"],
    "Software Engineer": ["java", "c++", "algorithms", "data structures", "git"],
    "Product Manager": ["communication", "roadmap planning", "agile", "jira", "stakeholder management"],
}

# Function to extract skills from PDF
def extract_skills_from_pdf(pdf_file):
    skills = set()
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ in ["SKILL", "GPE", "WORK_OF_ART", "LANGUAGE"]:  # Adjust labels as necessary
                skills.add(ent.text.lower())
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
    return list(skills)

# Function to match skills
def match_skills(user_skills, role_skills):
    matched = list(set(user_skills) & set(role_skills))
    missing = list(set(role_skills) - set(user_skills))
    return matched, missing

# Function to recommend skills
def recommend_skills(missing_skills, all_skills):
    recommendations = {}
    for skill in missing_skills:
        try:
            similarities = util.cos_sim(model.encode(skill), model.encode(all_skills))
            similar_skills = [all_skills[i] for i in similarities.argsort(descending=True)[:3]]
            recommendations[skill] = similar_skills
        except Exception:
            recommendations[skill] = []
    return recommendations

# Streamlit App UI
st.set_page_config(page_title="Resume Skill Matcher", layout="wide")
st.title("Resume Skill Matcher")

# Resume Upload
uploaded_file = st.file_uploader("Upload your Resume (PDF format)", type=["pdf"])
if uploaded_file:
    extracted_skills = extract_skills_from_pdf(uploaded_file)
    st.write("### Extracted Skills from Resume:")
    st.write(extracted_skills)

    # Job Role Selection
    selected_role = st.selectbox("Select Job Role:", list(job_skills.keys()))
    if selected_role:
        role_skills = job_skills[selected_role]
        matched, missing = match_skills(extracted_skills, role_skills)

        st.write("### Skills Matched:")
        st.write(matched)

        st.write("### Missing Skills:")
        st.write(missing)

        # Recommend Skills
        all_available_skills = sum(job_skills.values(), [])
        recommendations = recommend_skills(missing, all_available_skills)

        st.write("### Recommended Skills:")
        for skill, recs in recommendations.items():
            st.write(f"- **{skill}**: {', '.join(recs)}")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit")
