---
title: Multimodal RAG App
emoji: 📚
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# 📄 Multimodal RAG Chatbot (Production-Ready)

[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/DeepXAi/Multimodal-RAG-app)

Chat with any PDF like ChatGPT — grounded in **text, tables, and images** using a fully containerized AI pipeline.

This project implements a **production-style Multimodal Retrieval Augmented Generation (RAG)** system with a **FastAPI backend**, **Streamlit frontend**, **Chroma vector DB**, and **Dockerized deployment**.

---

## 🚀 Architecture

User (Browser)
      │
      ▼
Streamlit Frontend (UI)
      │  REST API
      ▼
FastAPI Backend (AI Engine)
      │
      ├── Multimodal PDF Parsing (Unstructured + OCR)
      ├── Chunking + Summarization
      ├── Embeddings (OpenAI)
      ├── Vector DB (Chroma)
      └── RAG Answer Generation


---

## ✨ Features

### 📄 Multimodal PDF Understanding
The system extracts and understands:

- Text paragraphs  
- Tables  
- Images  
- Diagrams  
- Charts  

Unlike normal RAG apps, this one supports **true multimodal ingestion**.

---

### 💬 Chat with Your Documents
Ask questions like:

- “What is this document about?”
- “Summarize the tables”
- “Explain the diagrams”

The LLM answers using **retrieved document chunks**, reducing hallucinations.

---


### 🔍 How the RAG Pipeline Works

### Step 1 — Document Partitioning
Uses **Unstructured** to extract:
- Paragraphs
- Tables
- Images

### Step 2 — Chunking
Chunks are grouped by semantic sections.

### Step 3 — AI Summarisation
Each chunk is summarized to improve retrieval quality.

### Step 4 — Embedding Generation
Chunks are embedded using **OpenAI Embeddings**.

### Step 5 — Vector Storage
Stored in **ChromaDB** for semantic search.

### Step 6 — Retrieval + Generation
User query → retrieve top chunks → generate grounded answer.


---

### ⚡ Production-Style Backend

Includes real backend engineering practices:

- Async job-based ingestion
- Status polling
- Clean REST API design
- Stateless frontend
- Global app state management
- Dockerized services

---

### 🐳 Fully Dockerized

Runs the entire stack in **one container**:

- FastAPI backend
- Streamlit frontend
- Chroma DB persistence
- OCR + PDF processing dependencies

Public Docker image available.

---

### 🛠 Tech Stack

| Layer | Technology |
|---|---|
| LLM | OpenAI GPT |
| Embeddings | OpenAI Embeddings |
| RAG Framework | LangChain |
| Vector Database | ChromaDB |
| Multimodal Parsing | Unstructured + OCR |
| Backend API | FastAPI |
| Frontend UI | Streamlit |
| Containerization | Docker |

---


---

### ⚙️ API Endpoints

Health Check
- GET /health

Upload & Ingest PDF
- POST /ingest

Check Ingestion Status
- GET /status/{job_id}


Ask Questions
- POST /query

---

### 🧪 Run Locally (Without Docker)

#### 1️⃣ Clone Repo
```bash
git clone https://github.com/YOUR_USERNAME/multimodal-rag.git
```

#### 2️⃣ Create Environment File
```bash
Create .env file:
OPENAI_API_KEY=your_api_key_here
```

#### 3️⃣ Run Backend
```bash
uvicorn backend.main:app --reload
```

* Backend runs at:

```bash
http://127.0.0.1:8000
```

#### 4️⃣ Run Frontend
```bash
streamlit run app.py
```

* Frontend runs at:
```bash
http://localhost:8501
```

### 🐳 Run with Docker (Recommended)
* Pull public image
```bash
docker pull deepam5708/multimodal-rag-app:final
```

* Run container
```bash
docker run --env-file .env -p 8000:8000 -p 8501:7860 deepam5708/multimodal-rag-app:final
```

* Open:
```bash
http://localhost:8501
```





