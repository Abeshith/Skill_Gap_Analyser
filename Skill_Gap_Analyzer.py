import streamlit as st
from transformers import LayoutLMForTokenClassification, LayoutLMTokenizer, pipeline
from PyPDF2 import PdfReader
import re

# Predefined skills for job roles
JOB_ROLES = {
    "Data Scientist": ["Python", "R", "Machine Learning", "Deep Learning", "Natural Language Processing", "SQL", "Statistics"],
    "Machine Learning Engineer": ["Python", "Machine Learning", "Deep Learning", "NLP", "TensorFlow", "PyTorch", "Scikit-learn"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "React", "Node.js", "Bootstrap", "Git"],
    "Cloud Engineer": ["AWS", "Azure", "Kubernetes", "Docker", "Terraform", "DevOps"],
}

# Streamlit app setup
st.set_page_config(page_title="Resume Analyzer", layout="wide")
st.title("📄 Resume Analyzer")

# Upload resume
uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"], key="resume")

# Select job role
job_role = st.selectbox("Select a Job Role:", options=["Choose"] + list(JOB_ROLES.keys()))

# Helper function to clean and preprocess text
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)  # Remove special characters
    return text

# Helper function to extract text using PyPDF2
def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Analyze button
if st.button("Analyze Resume"):
    if not uploaded_file or job_role == "Choose":
        st.error("Please upload a resume and select a job role!")
    else:
        try:
            # Step 1: Extract text from the uploaded PDF
            resume_text = extract_text_from_pdf(uploaded_file)
            resume_text = preprocess_text(resume_text)

            # Step 2: Load the LayoutLM model and tokenizer for semantic understanding
            tokenizer = LayoutLMTokenizer.from_pretrained("microsoft/layoutlm-base-uncased")
            model = LayoutLMForTokenClassification.from_pretrained("microsoft/layoutlm-base-uncased")

            # Tokenize and analyze text
            inputs = tokenizer(resume_text, return_tensors="pt", truncation=True, padding=True)
            outputs = model(**inputs)

            # Step 3: Extract relevant skills for the selected job role
            required_skills = JOB_ROLES[job_role]

            # Step 4: Match skills based on semantic similarity (simple matching here)
            matched_skills = [skill for skill in required_skills if skill.lower() in resume_text]
            missing_skills = list(set(required_skills) - set(matched_skills))

            # Step 5: Display results
            st.write("### Skills Matched:")
            st.write(matched_skills if matched_skills else "No skills matched.")

            st.write("### Missing Skills:")
            st.write(missing_skills if missing_skills else "No missing skills. Great job!")

            # Step 6: Recommend improvements for missing skills
            if missing_skills:
                st.write("### Recommended Skills for Improvement:")
                for skill in missing_skills:
                    st.write(f"- {skill}: Strengthen your knowledge and practical applications in {skill}.")
        except Exception as e:
            st.error(f"An error occurred while processing the resume: {str(e)}")
