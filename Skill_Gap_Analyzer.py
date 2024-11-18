import streamlit as st
import pdfplumber
import openai
from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

# Mocked skills for job roles (can be extended or fetched from a database)
JOB_ROLES = {
    "Data Scientist": ["Python", "Machine Learning", "Deep Learning", "SQL", "Statistics"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "React", "Node.js"],
    "Cloud Engineer": ["AWS", "Azure", "Kubernetes", "Docker", "DevOps"]
}

# OpenAI API setup (replace this with your actual API key)
openai.api_key = "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"

# Set up the Streamlit app
st.set_page_config(page_title="Resume Analyzer", layout="wide")

# Custom UI for uploading and job role selection
st.markdown("""
    <style>
    .title { font-size: 2rem; text-align: center; color: #4CAF50; margin-bottom: 2rem; }
    .upload { margin: 1rem auto; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">📄 Resume Analyzer</div>', unsafe_allow_html=True)

# Upload resume
uploaded_file = st.file_uploader("Upload your resume (PDF only)", type=["pdf"], key="resume")

# Select job role
job_role = st.selectbox("Select a Job Role:", options=["Choose"] + list(JOB_ROLES.keys()))

# Analyze button
if st.button("Analyze Resume"):
    if not uploaded_file or job_role == "Choose":
        st.error("Please upload a resume and select a job role!")
    else:
        # Step 1: Extract text from the resume using pdfplumber
        with pdfplumber.open(uploaded_file) as pdf:
            resume_text = " ".join(page.extract_text() for page in pdf.pages)

        # Step 2: Analyze skills using simple text matching
        required_skills = JOB_ROLES[job_role]
        extracted_skills = [skill for skill in required_skills if skill.lower() in resume_text.lower()]

        # Step 3: Display matched skills
        st.write("### Skills Matched:")
        st.write(extracted_skills)

        # Step 4: Display missing skills
        missing_skills = list(set(required_skills) - set(extracted_skills))
        st.write("### Missing Skills:")
        st.write(missing_skills)

        # Step 5: Recommend missing skills using OpenAI API (gpt-3.5-turbo)
        if missing_skills:
            st.write("### Skill Recommendations:")
            for skill in missing_skills:
                prompt = f"Recommend skills related to {skill}."
                response = openai.Completion.create(
                    model="gpt-3.5-turbo",  # Using GPT-3.5-turbo instead of text-davinci-003
                    prompt=prompt,
                    max_tokens=50,
                    temperature=0.6
                )
                recommendations = response.choices[0].text.strip()
                st.write(f"**{skill}:** {recommendations}")
        else:
            st.write("No missing skills found. Great job!")

        # Optional: Use Langchain's RAG (retrieval-augmented generation) to answer any job-specific queries
        if st.button("Ask about Job Role"):
            query = st.text_input("Ask anything about the job role:")
            if query:
                # Use Langchain to create a retrieval-based answer for job role related queries
                documents = [resume_text]  # In a real app, you'd load documents into Langchain's FAISS
                vectorstore = FAISS.from_documents(documents, OpenAIEmbeddings())
                retriever = vectorstore.as_retriever()
                qa_chain = RetrievalQA.from_chain_type(
                    llm=openai.Completion.create,
                    retriever=retriever
                )
                answer = qa_chain.run(query)
                st.write(f"### Answer: {answer}")
