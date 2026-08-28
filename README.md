Smart Resume Analyzer & Interview Assistant

Overview

The Smart Resume Analyzer & Interview Assistant is an AI-powered web application built using Streamlit, LangChain, FAISS, Sentence Transformers, and Ollama. It helps job seekers analyze their resumes against a job description, identify missing skills, generate interview questions, and interact with their documents through a Retrieval-Augmented Generation (RAG) chatbot.

Unlike traditional resume analyzers, this project uses a local Large Language Model (LLM) with RAG, ensuring that responses are generated based on the uploaded resume and job description rather than relying solely on the model's pre-trained knowledge.

---

Features

1) Upload Resume in PDF or DOCX format.

2) Paste any Job Description.

3) Generate Resume Match Score.

Identify Missing Technical and Soft Skills.

* Receive ATS Optimization Recommendations.

* Generate Technical Interview Questions.

* Generate HR & Behavioral Interview Questions.

* Chat with your Resume and Job Description using RAG.

* View Retrieved Context Chunks from the FAISS vector database.

* Runs completely locally using Ollama (No OpenAI API required).

---

 Project Architecture
<img width="1080" height="1457" alt="WhatsApp Image 2026-08-27 at 7 21 01 PM" src="https://github.com/user-attachments/assets/251ed08f-50c6-4089-ba66-71c305e3c1c6" />

---

Tech Stack

Technology	Purpose

Streamlit	Frontend UI

LangChain	LLM Orchestration

Ollama	Local LLM Inference

Qwen2.5	Large Language Model

FAISS	Vector Database

Sentence Transformers	Text Embeddings

PyMuPDF	PDF Text Extraction

Docx2txt	DOCX Text Extraction

Python	Backend

---

How the Project Works

Step 1: Upload Documents

The user uploads a resume (PDF/DOCX) and pastes a job description into the Streamlit interface.


---

Step 2: Text Extraction

The application extracts text from the uploaded files.

PDF → PyMuPDF

DOCX → Docx2txtLoader


The extracted content is converted into plain text.

---

Step 3: Document Chunking

Large documents cannot be processed efficiently as one block.

Therefore, the application uses:

RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)

The documents are divided into smaller overlapping chunks.

Example:

Resume

↓

Chunk 1

↓

Chunk 2

↓

Chunk 3

The overlap preserves context between chunks and improves retrieval quality.


---

Step 4: Embedding Generation

Each chunk is converted into a numerical vector using the all-MiniLM-L6-v2 Sentence Transformer model.

Example:

"I have experience in Python."

↓

[-0.21, 0.43, 0.92, ...]

These embeddings capture the semantic meaning of the text.

---

Step 5: Vector Storage

The generated embeddings are stored in a FAISS Vector Database.

FAISS enables fast similarity search by comparing vector distances instead of exact keywords.

---

Step 6: Resume Analysis

When the user clicks Generate Match Report, the application sends the resume and job description to the local Qwen2.5 model through Ollama.

The model generates:

Resume Match Score

Missing Skills

ATS Keyword Recommendations

Overall Summary

---

Step 7: Interview Question Generation

The application generates:

Technical Questions

Questions are created based on:

Candidate skills

Job requirements

Missing technologies


Behavioral Questions

STAR-method interview questions are generated using the candidate's experience and target role.

---

Step 8: RAG Chat Assistant

The chatbot follows the Retrieval-Augmented Generation (RAG) workflow.

Retrieval

When the user asks a question:

How well does my resume match leadership requirements?

The application:

1. Converts the question into an embedding.


2. Searches the FAISS vector database.


3. Retrieves the top 3 most relevant chunks.

---

Augmentation

The retrieved chunks are combined into a context.

Example:

Resume Chunk

Job Description Chunk

Resume Chunk

---

Generation

The context and the user's question are sent to the Qwen2.5 model.

The model is instructed to answer only using the retrieved context.

This minimizes hallucinations and improves response accuracy.

---

Project Structure
<img width="1080" height="741" alt="WhatsApp Image 2026-08-28 at 5 16 56 PM" src="https://github.com/user-attachments/assets/d24b4ead-2412-4d56-92b7-f85c42a51de5" />


---

Why RAG?

Traditional LLMs answer questions using their pre-trained knowledge.

RAG improves this process by retrieving relevant information from the uploaded documents before generating an answer.

Benefits

More accurate responses

Reduced hallucinations

Context-aware answers

Explainable outputs

Uses the user's own documents



---

Future Enhancements

Support multiple resume uploads.

ATS score visualization with charts.

Multi-language resume support.

Export analysis reports as PDF.

Resume improvement suggestions.

Voice-enabled interview practice.

Integration with cloud LLMs (OpenAI, Gemini, Claude).

---

Installation

Clone the repository

git clone https://github.com/your-username/smart-resume-analyzer.git
cd smart-resume-analyzer

Install dependencies

pip install -r requirements.txt

Install Ollama

Download and install Ollama from:

https://ollama.com/download

Pull the Qwen2.5 model:

ollama pull qwen2.5

Run the application

streamlit run app.py

---

Author

Rahul

---

Key Learning Outcomes

Built a complete RAG (Retrieval-Augmented Generation) pipeline.

Implemented semantic search using FAISS and Sentence Transformers.

Integrated a local LLM (Qwen2.5) through Ollama.

Developed an interactive web interface using Streamlit.

Applied LangChain for document handling, prompt engineering, and retrieval workflows.

Created an end-to-end AI application for resume analysis, interview preparation, and document-based question answering.
