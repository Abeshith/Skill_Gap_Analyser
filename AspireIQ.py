import streamlit as st
import pdfplumber
from fuzzywuzzy import fuzz
import requests

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

# Function to get course recommendations from Llama API
def get_course_recommendations(skill):
    try:
        response = requests.post(
            "https://api.llama-api.com/v1/completions",
            headers={"Authorization": "Bearer LA-1b496db6f37f456dbf37187c3b05df0e8920b9aacec24c6b800d9929ebcfac91"},
            json={
                "model": "llama-3-70b-instruct",
                "prompt": f"Recommend online courses to learn {skill}.",
                "max_tokens": 100,
            },
        )
        if response.status_code == 200:
            courses = response.json().get("choices", [])
            if courses:
                return [course['text'].strip() for course in courses]
            else:
                return ["No course recommendations found."]
        else:
            return [f"Error fetching course recommendations: {response.status_code}"]
    except Exception as e:
        return [f"Error: {str(e)}"]

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

        # Step 4: Recommend related courses for missing skills
        if missing_skills:
            st.subheader("Course Recommendations")
            for skill in missing_skills:
                st.write(f"**{skill.capitalize()}**")
                # Fetch course recommendations from Llama API
                courses = get_course_recommendations(skill)
                for course in courses:
                    st.write(f"- {course}")
