import streamlit as st
import PyPDF2
from keybert import KeyBERT
from sentence_transformers import SentenceTransformer, util
import nltk
import subprocess

# Download NLTK resources
nltk.download("punkt")

# Initialize KeyBERT and SentenceTransformer
kw_model = KeyBERT()
model = SentenceTransformer('all-MiniLM-L6-v2')

# Predefined skills for job roles
job_skills = {
    "Data Scientist": ["python", "machine learning", "data analysis", "sql", "deep learning", "statistics"],
    "Software Engineer": ["java", "c++", "algorithms", "data structures", "git", "software design"],
    "Product Manager": ["communication", "roadmap planning", "agile", "jira", "stakeholder management", "marketing"],
}

# Function to extract skills from PDF using KeyBERT
def extract_skills_from_pdf(pdf_file):
    skills = set()
    try:
        # Read PDF content
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        # Extract keywords (skills) using KeyBERT
        keywords = kw_model.extract_keywords(text, top_n=20, keyphrase_ngram_range=(1, 1))
        skills = [kw[0].lower() for kw in keywords]  # Extract skill names and make them lowercase
    except Exception as e:
        st.error(f"Error processing PDF: {e}")
    return skills

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

# Function to suggest courses for missing skills
def recommend_courses(missing_skills):
    courses = {
        "python": "Python for Data Science on Coursera",
        "machine learning": "Machine Learning by Andrew Ng on Coursera",
        "sql": "SQL for Data Science on Coursera",
        "deep learning": "Deep Learning Specialization on Coursera",
        "java": "Java Programming on Udemy",
        "c++": "C++ Programming on Udemy",
        "agile": "Agile Project Management on Udemy",
        "communication": "Communication Skills for Leaders on LinkedIn Learning",
        "stakeholder management": "Stakeholder Management on LinkedIn Learning"
    }
    course_recommendations = {}
    for skill in missing_skills:
        if skill in courses:
            course_recommendations[skill] = courses[skill]
    return course_recommendations

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

        # Recommend Courses for Missing Skills
        course_recommendations = recommend_courses(missing)
        st.write("### Recommended Courses for Missing Skills:")
        for skill, course in course_recommendations.items():
            st.write(f"- **{skill}**: {course}")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit")
