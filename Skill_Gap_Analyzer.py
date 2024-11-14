import streamlit as st
from transformers import pipeline
import PyPDF2

# Define job roles and required skills
job_roles = {
    "Data Scientist": ["Python", "Machine Learning", "Statistics", "Data Analysis", "Deep Learning"],
    "Software Engineer": ["Java", "Data Structures", "Algorithms", "System Design", "Databases"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "React", "Web Design"],
    "Project Manager": ["Project Management", "Agile", "Scrum", "Team Management", "Risk Management"],
    "Cloud Engineer": ["AWS", "Azure", "Cloud Architecture", "DevOps", "Docker"],
    "AI Engineer": ["Python", "Machine Learning", "Deep Learning", "NLP", "TensorFlow"],
    "Product Manager": ["Product Development", "Market Research", "Data Analysis", "UX Design", "Roadmapping"],
    "Cybersecurity Specialist": ["Network Security", "Cryptography", "Penetration Testing", "Firewalls", "Ethical Hacking"],
    "Data Analyst": ["Excel", "SQL", "Python", "Data Visualization", "Statistics"],
    "Business Analyst": ["Business Analysis", "Data Analysis", "SQL", "Communication", "Project Management"]
}

# Load the Hugging Face model for skill extraction (using DistilBERT for faster performance)
@st.cache_resource
def load_model():
    return pipeline("zero-shot-classification", model="distilbert-base-uncased")

model = load_model()

# Course recommendations for each skill gap
course_recommendations = {
    "Python": ["https://www.udemy.com/course/python-for-beginners/", "https://www.youtube.com/watch?v=_uQrJ0TkZlc"],
    "Machine Learning": ["https://www.udacity.com/course/intro-to-machine-learning--ud120", "https://www.youtube.com/watch?v=Gv9_4yMHFhI"],
    "Statistics": ["https://www.coursera.org/learn/statistical-inference", "https://www.youtube.com/watch?v=xxpc-HPKN28"],
    # Add additional skills and corresponding courses
}

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to extract skills from resume using Hugging Face model
def extract_resume_skills(resume_text, required_skills):
    results = model(resume_text, candidate_labels=required_skills)
    extracted_skills = [label for label, score in zip(results["labels"], results["scores"]) if score > 0.3]
    return extracted_skills

# Function to identify skill gaps
def get_skill_gaps(extracted_skills, required_skills):
    return [skill for skill in required_skills if skill not in extracted_skills]

# Function to recommend courses based on skill gaps
def recommend_courses(skill_gaps):
    recommendations = {}
    for skill in skill_gaps:
        if skill in course_recommendations:
            recommendations[skill] = course_recommendations[skill]
    return recommendations

# Streamlit interface
st.title("Resume Skill Gap Analyzer")

uploaded_file = st.file_uploader("Upload your resume (PDF or Text)", type=["pdf", "txt"])
selected_role = st.selectbox("Select Job Role", list(job_roles.keys()))

if uploaded_file and selected_role:
    if uploaded_file.type == "application/pdf":
        resume_text = extract_text_from_pdf(uploaded_file)
    else:
        resume_text = uploaded_file.read().decode("utf-8")

    required_skills = job_roles[selected_role]
    extracted_skills = extract_resume_skills(resume_text, required_skills)
    skill_gaps = get_skill_gaps(extracted_skills, required_skills)
    course_suggestions = recommend_courses(skill_gaps)

    st.subheader("Skills Identified in Resume:")
    st.write(", ".join(extracted_skills))

    st.subheader("Skill Gaps for the Job Role:")
    st.write(", ".join(skill_gaps))

    st.subheader("Course Recommendations for Skill Gaps:")
    for skill, courses in course_suggestions.items():
        st.write(f"**{skill}**:")
        for course in courses:
            st.write(f"- [Course]({course})")
