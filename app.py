import os
import tempfile

import pymupdf
import streamlit as st
from langchain_community.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain.schema import Document

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

# --- session state -----------------------------------------------------
# streamlit reruns top to bottom on every interaction, so anything that
# needs to survive a click has to live here instead of a local variable
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "job_description" not in st.session_state:
    st.session_state.job_description = ""
if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# --- models --------------------------------------------------------------
# cached so we're not reloading the embedding model / reconnecting to
# ollama on every single button click
@st.cache_resource
def load_embedding_model():
    return SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")


@st.cache_resource
def load_llm():
    return ChatOllama(model="qwen2.5:latest", temperature=0.2)


embeddings = load_embedding_model()
llm = load_llm()


def extract_text_from_file(uploaded_file):
    if uploaded_file.name.lower().endswith(".pdf"):
        doc = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        return text

    if uploaded_file.name.lower().endswith(".docx"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        try:
            loader = Docx2txtLoader(tmp_path)
            pages = loader.load()
            return "\n".join(p.page_content for p in pages)
        finally:
            os.remove(tmp_path)

    raise ValueError("Unsupported file type — please upload a PDF or DOCX")


def build_vector_index(resume_text, jd_text):
    docs = [
        Document(page_content=resume_text, metadata={"source": "Resume"}),
        Document(page_content=jd_text, metadata={"source": "Job Description"}),
    ]

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    return FAISS.from_documents(chunks, embeddings)


# --- sidebar: upload + ingestion ---------------------------------------
with st.sidebar:
    st.header("Setup")

    uploaded_resume = st.file_uploader("Upload your resume", type=["pdf", "docx"])
    job_description = st.text_area("Paste the job description", height=250)

    if st.button("Run Analysis", type="primary"):
        if uploaded_resume is None or not job_description.strip():
            st.warning("Need both a resume and a job description before running this.")
        else:
            with st.spinner("Reading resume and building index..."):
                resume_text = extract_text_from_file(uploaded_resume)
                st.session_state.resume_text = resume_text
                st.session_state.job_description = job_description
                st.session_state.vector_store = build_vector_index(resume_text, job_description)
                st.session_state.chat_history = []
            st.success("Done — resume indexed and ready.")
            st.rerun()


# --- main area: tabs -----------------------------------------------------
tab_analysis, tab_questions, tab_chat = st.tabs(
    ["Resume Analysis", "Interview Questions", "Chat Assistant"]
)

with tab_analysis:
    st.subheader("Match Report")

    if st.button("Generate Match Report"):
        if not st.session_state.resume_text:
            st.warning("Upload a resume and run the analysis in the sidebar first.")
        else:
            prompt = f"""You are reviewing a candidate's resume against a job description.

Resume:
{st.session_state.resume_text}

Job Description:
{st.session_state.job_description}

Give me:
1. A match score out of 100
2. Key skills or requirements the resume is missing
3. ATS (applicant tracking system) recommendations
4. A short overall summary
"""
            with st.spinner("Analyzing..."):
                response = llm.invoke(prompt)
                st.session_state.analysis_result = response.content

    if st.session_state.analysis_result:
        st.markdown(st.session_state.analysis_result)


with tab_questions:
    st.subheader("Interview Question Generator")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Generate Technical Questions"):
            if not st.session_state.resume_text:
                st.warning("Run the analysis in the sidebar first.")
            else:
                prompt = f"""Based on this resume and job description, write 5 technical
interview questions. Lean toward the skills that match well, but include a
couple that probe the gaps between the two.

Resume:
{st.session_state.resume_text}

Job Description:
{st.session_state.job_description}
"""
                with st.spinner("Generating..."):
                    response = llm.invoke(prompt)
                    st.markdown(response.content)

    with col2:
        if st.button("Generate HR Questions"):
            if not st.session_state.resume_text:
                st.warning("Run the analysis in the sidebar first.")
            else:
                prompt = f"""Write 5 behavioral interview questions in STAR format
(Situation, Task, Action, Result), tailored to this candidate's background.

Resume:
{st.session_state.resume_text}

Job Description:
{st.session_state.job_description}
"""
                with st.spinner("Generating..."):
                    response = llm.invoke(prompt)
                    st.markdown(response.content)


with tab_chat:
    st.subheader("Ask about the resume or job description")

    for turn in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(turn["question"])
        with st.chat_message("assistant"):
            st.write(turn["answer"])
            with st.expander("Sources"):
                for src in turn["sources"]:
                    st.caption(f"{src['source']} · distance {src['score']:.2f}")
                    st.text(src["content"])

    user_query = st.chat_input("Ask a question...")

    if user_query:
        if st.session_state.vector_store is None:
            st.warning("Please run document ingestion first (sidebar → Run Analysis).")
        else:
            with st.chat_message("user"):
                st.write(user_query)

            results = st.session_state.vector_store.similarity_search_with_score(
                user_query, k=3
            )

            context_blocks = []
            sources = []
            for doc, score in results:
                context_blocks.append(f"[{doc.metadata['source']}]\n{doc.page_content}")
                sources.append(
                    {
                        "source": doc.metadata["source"],
                        "score": score,
                        "content": doc.page_content,
                    }
                )
            context = "\n\n---\n\n".join(context_blocks)

            prompt = f"""Answer the question using ONLY the context below. If the
context doesn't contain the answer, say so directly instead of guessing.

Context:
{context}

Question: {user_query}
"""
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = llm.invoke(prompt)
                    st.write(response.content)
                    with st.expander("Sources"):
                        for src in sources:
                            st.caption(f"{src['source']} · distance {src['score']:.2f}")
                            st.text(src["content"])

            st.session_state.chat_history.append(
                {
                    "question": user_query,
                    "answer": response.content,
                    "sources": sources,
                }
            )