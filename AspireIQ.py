import streamlit as st
import pdfplumber
from transformers import pipeline
from fuzzywuzzy import fuzz
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Define job roles and corresponding skill keywords
JOB_ROLES = {
   "Data Scientist": ["Python", "Machine Learning", "Deep Learning", "SQL", "Statistics", "TensorFlow", "Scikit-learn", "Pandas", "NumPy"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "React", "Node.js", "Bootstrap", "Tailwind CSS", "Angular"],
    "Cloud Engineer": ["AWS", "Azure", "Kubernetes", "Docker", "DevOps", "Terraform", "Ansible", "Google Cloud Platform"],
    "AI Engineer": ["Python", "Deep Learning", "NLP", "TensorFlow", "PyTorch", "Transformers", "OpenCV", "Reinforcement Learning"],
    "Mobile App Developer": ["Kotlin", "Swift", "Flutter", "React Native", "Java", "Dart", "Objective-C"],
    "Cybersecurity Analyst": ["Penetration Testing", "Ethical Hacking", "Cryptography", "Network Security", "SIEM", "Firewalls", "Incident Response"],
    "DevOps Engineer": ["CI/CD", "Jenkins", "Git", "Kubernetes", "Docker", "AWS", "Terraform", "Monitoring Tools"],
    "Software Tester": ["Selenium", "TestNG", "JIRA", "Manual Testing", "Automated Testing", "Performance Testing", "API Testing"],
    "Database Administrator": ["SQL", "NoSQL", "MongoDB", "PostgreSQL", "Oracle", "Database Optimization", "Backup & Recovery"],
    "Blockchain Developer": ["Solidity", "Ethereum", "Smart Contracts", "Hyperledger", "Consensus Algorithms", "Cryptography", "Web3"],
    "UI/UX Designer": ["Figma", "Sketch", "Adobe XD", "User Research", "Wireframing", "Prototyping", "Interaction Design"],
    "Game Developer": ["Unity", "Unreal Engine", "C#", "C++", "Game Physics", "Blender", "3D Modeling"],
    "Machine Learning Engineer": ["Python", "R", "TensorFlow", "PyTorch", "Deep Learning", "Natural Language Processing", "Keras", "NLP"],
    "Product Manager": ["Agile Methodologies", "Scrum", "Product Lifecycle", "Market Research", "Stakeholder Management", "JIRA", "Roadmaps"],
    "Network Engineer": ["Cisco Networking", "Routing & Switching", "Firewall Configuration", "LAN/WAN", "TCP/IP", "VPN", "Network Security"],
}

# Set up Streamlit
st.set_page_config(page_title="Resume Analyzer", layout="wide")
st.title("📄 Resume Analyzer")

# Upload Resume
uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"])

# Select Job Role
job_role = st.selectbox("Select a Job Role:", options=["Choose"] + list(JOB_ROLES.keys()))

# Gemini API Configuration
GEMINI_API_KEY = "AIzaSyDqwe1AHD2ftF-0D2S2O3-fsWuL8wVMe54"  # Your provided API key

# Function to fetch courses using LangChain and Gemini API
def fetch_courses_with_langchain(skill):
    llm = OpenAI(temperature=0.5, api_key=GEMINI_API_KEY)
    prompt = PromptTemplate(
        input_variables=["skill"],
        template="Find 5 best courses for {skill} and include thumbnail URL, title, description, and course link."
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(skill)
    return response

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

        # Step 4: Recommend courses for missing skills
        if missing_skills:
            st.subheader("Skill Recommendations")
            for skill in missing_skills:
                st.write(f"**Courses for {skill}:**")
                course_data = fetch_courses_with_langchain(skill)
                if course_data:
                    st.markdown(course_data, unsafe_allow_html=True)
                else:
                    st.write("No courses found for this skill.")
