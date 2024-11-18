import streamlit as st
import pdfplumber
import openai
from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

# Set OpenAI API Key
openai.api_key = "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"

# Mocked skills for job roles (can be extended or fetched from a database)
JOB_ROLES = {
    "Data Scientist": ["Python", "Machine Learning", "Deep Learning", "SQL", "Statistics"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "React", "Node.js"],
    "Cloud Engineer": ["AWS", "Azure", "Kubernetes", "Docker", "DevOps"]
}

# Set up Streamlit app layout
st.set_page_config(page_title="Resume Analyzer", layout="wide")

st.markdown("<h1 style='text-align: center;'>📄 Resume Analyzer</h1>", unsafe_allow_html=True)

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

        # Step 2: Create a document loader and load the resume text for processing
        documents = [resume_text]
        
        # Set up OpenAI embeddings and FAISS vector store
        embeddings = OpenAIEmbeddings()
        docsearch = FAISS.from_texts(documents, embeddings)

        # Step 3: Set up Retrieval-based QA Chain with LangChain
        qa_chain = RetrievalQA.from_chain_type(llm=openai.ChatCompletion.create, retriever=docsearch.as_retriever())

        # Step 4: Query the resume text for skills
        query = "What skills does this resume have?"
        result = qa_chain.run(query)

        # Step 5: Analyze skills using simple text matching with the job role
        required_skills = JOB_ROLES[job_role]
        extracted_skills = [skill for skill in required_skills if skill.lower() in result.lower()]

        # Step 6: Display matched skills
        st.write("### Skills Matched:")
        st.write(extracted_skills)

        # Step 7: Display missing skills
        missing_skills = list(set(required_skills) - set(extracted_skills))
        st.write("### Missing Skills:")
        st.write(missing_skills)

        # Step 8: Recommend missing skills using OpenAI's GPT for context-based recommendations
        if missing_skills:
            st.write("### Skill Recommendations:")
            for skill in missing_skills:
                prompt = f"Recommend skills related to {skill}."

                # Use OpenAI's model to generate skill recommendations
                response = openai.Completion.create(
                    model="text-davinci-003",  # You can choose the model you prefer
                    prompt=prompt,
                    max_tokens=50,
                    temperature=0.6
                )
                recommendations = response.choices[0].text.strip()
                st.write(f"**{skill}:** {recommendations}")
        else:
            st.write("No missing skills found. Great job!")
