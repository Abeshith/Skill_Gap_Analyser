import streamlit as st
import pdfplumber
from fuzzywuzzy import fuzz
import openai
from PIL import Image
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

# OpenAI API Key
openai.api_key = "your_openai_api_key"

# Function to recommend courses for missing skills
def recommend_courses(skill):
    prompt = f"Recommend 5 online courses for learning {skill}. Provide the course name, platform, and a link to the course."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Using gpt-3.5-turbo for this case
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        course_recommendations = response['choices'][0]['message']['content'].strip().split("\n")
        return course_recommendations
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

        # Step 4: Recommend related skills for missing ones
        if missing_skills:
            st.subheader("Missing Skill Recommendations")
            for skill in missing_skills:
                st.write(f"### Courses for **{skill.capitalize()}**")
                courses = recommend_courses(skill)
                
                # Display courses as YouTube-like thumbnails
                cols = st.columns(3)
                for i, course in enumerate(courses):
                    if i < 5:
                        with cols[i % 3]:  # 3 columns for YouTube-style thumbnails
                            course_info = course.split(" - ")
                            if len(course_info) == 3:
                                course_name, platform, link = course_info
                                # Display the thumbnail with title and link
                                st.image("https://via.placeholder.com/150", caption=course_name, use_column_width=True)  # Placeholder image
                                st.markdown(f"[{course_name}]({link}) - {platform}")
