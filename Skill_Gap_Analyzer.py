import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import PyPDF2

# Initialize LangChain with Gemini API
google_api_key = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-pro", google_api_key=google_api_key)

# Define job roles and required skills
job_roles = {
    "Data Scientist": ["Python", "Machine Learning", "Data Analysis"],
    "Software Engineer": ["Java", "Data Structures", "Algorithms", "System Design"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "React", "Web Design"],
    "Project Manager": ["Project Management", "Agile", "Scrum", "Team Management"],
    "Cloud Engineer": ["AWS", "Azure", "Cloud Architecture", "DevOps", "Docker"],
    "AI Engineer": ["Python", "Machine Learning", "Deep Learning", "NLP", "TensorFlow"],
    "Product Manager": ["Product Development", "Market Research", "Data Analysis", "UX Design"],
    "Cybersecurity Specialist": ["Network Security", "Cryptography", "Penetration Testing", "Firewalls"],
    "Data Analyst": ["Excel", "SQL", "Python", "Data Visualization", "Statistics"],
    "Business Analyst": ["Business Analysis", "Data Analysis", "SQL", "Communication"]
}

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Function to extract skills from resume using LangChain
def extract_resume_skills(resume_text, required_skills):
    prompt = f"Identify the skills from the following resume text:\n{resume_text}\n\nSkills to look for: {', '.join(required_skills)}"
    response = llm.invoke(prompt)
    extracted_skills = response['text'].split(", ")
    return extracted_skills

# Function to identify skill gaps
def get_skill_gaps(extracted_skills, required_skills):
    return [skill for skill in required_skills if skill not in extracted_skills]

# Function to recommend courses based on skill gaps
def recommend_courses(skill_gaps):
    course_recommendations = {
        "Python": ["https://www.udemy.com/course/python-for-beginners/", "https://www.youtube.com/watch?v=_uQrJ0TkZlc"],
        "Machine Learning": ["https://www.udacity.com/course/intro-to-machine-learning--ud120", "https://www.youtube.com/watch?v=Gv9_4yMHFhI"],
        "Data Analysis": ["https://www.coursera.org/learn/data-analysis", "https://www.youtube.com/watch?v=5oG6zv5g0gM"],
        "Java": ["https://www.udemy.com/course/java-programming/", "https://www.youtube.com/watch?v=grEKMHpHj9o"],
        "Cloud Architecture": ["https://www.udemy.com/course/aws-certified-solutions-architect-associate/", "https://www.youtube.com/watch?v=Ia-UEYYR44s"],
        "React": ["https://www.udemy.com/course/react-the-complete-guide-incl-redux/", "https://www.youtube.com/watch?v=DLX62G4lc44"],
        "Penetration Testing": ["https://www.udemy.com/course/learn-ethical-hacking-from-scratch/", "https://www.youtube.com/watch?v=5ZtZxuR7kGE"],
        # Add additional skills and corresponding courses
    }
    recommendations = {}
    for skill in skill_gaps:
        if skill in course_recommendations:
            recommendations[skill] = course_recommendations[skill]
    return recommendations

# Streamlit interface
st.title("Resume Skill Gap Analyzer")

# File uploader for the resume
uploaded_file = st.file_uploader("Upload your resume (PDF or Text)", type=["pdf", "txt"])

# Select the job role
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

    # Displaying results
    st.subheader("Skills Identified in Resume:")
    st.write(", ".join(extracted_skills))

    st.subheader("Skill Gaps for the Job Role:")
    st.write(", ".join(skill_gaps))

    st.subheader("Course Recommendations for Skill Gaps:")
    for skill, courses in course_suggestions.items():
        st.write(f"**{skill}**:")
        for course in courses:
            st.write(f"- [Course]({course})")
