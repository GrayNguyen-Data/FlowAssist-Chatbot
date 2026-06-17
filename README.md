# FlowAssist Chatbot

Enterprise RAG Chatbot for internal document question-answering, built with **FastAPI**, **React**, **TiDB Vector Search**, **Redis**, **MinIO**, **Groq LLM**, and **Docker**.

FlowAssist helps users upload business documents, extract knowledge, retrieve relevant context, and generate accurate answers using a Retrieval-Augmented Generation pipeline. The system also supports conversation memory, feedback tracking, and ticket creation when users report incorrect answers.

---

## Overview

FlowAssist is designed as a production-oriented AI assistant for enterprise knowledge management.

Instead of answering only from the base LLM, the chatbot retrieves information from uploaded documents and injects the most relevant context into the prompt before generating a response. This helps reduce hallucination and makes answers more grounded in company-specific data.

---

## Key Features

* Document-based question answering using RAG
* PDF, DOCX, TXT, MD, CSV, and JSON ingestion
* Text normalization, chunking, embedding, and vector storage
* Hybrid retrieval with vector search and keyword fallback
* Reciprocal Rank Fusion for result merging
* Conversation memory using Redis
* LLM integration with Groq
* Feedback and ticket workflow for wrong answers
* MinIO object storage for uploaded documents
* FastAPI REST API backend
* React/Vite frontend
* Docker Compose deployment
* Nginx reverse proxy
* MCP-compatible endpoint for external tool integration

---

## Tech Stack

| Layer              | Technology                                |
| ------------------ | ----------------------------------------- |
| Frontend           | React, Vite, Axios, Zustand, React Router |
| Backend            | FastAPI, Python 3.11                      |
| LLM                | Groq / LangChain Groq                     |
| Embedding          | Sentence Transformers                     |
| Vector Database    | TiDB Vector Search                        |
| Cache / Memory     | Redis                                     |
| Object Storage     | MinIO                                     |
| Reverse Proxy      | Nginx                                     |
| Containerization   | Docker, Docker Compose                    |
| Database Migration | Alembic                                   |
| API Style          | REST API + MCP endpoint                   |

---
## RAG Pipeline

### 1. Document Upload

Users upload documents through the frontend or API. Files are stored in MinIO and metadata is saved for later processing.

### 2. Text Extraction

The ingestion service extracts text from supported formats:

* PDF
* DOCX
* TXT
* Markdown
* CSV
* JSON

### 3. Chunking

Documents are split into overlapping chunks to keep each piece of context small enough for embedding and retrieval.

Default configuration:

```env
CHUNKING_SIZE=500
CHUNKING_OVERLAP=50
```

### 4. Embedding

Each chunk is converted into a vector using Sentence Transformers.

Default model:

```env
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_VECTOR_SIZE=384
```

### 5. Vector Storage

Embeddings are stored in TiDB and searched using cosine distance.

### 6. Hybrid Retrieval

For each user query, the retrieval service performs:

* query normalization
* query expansion
* vector search
* keyword fallback search
* Reciprocal Rank Fusion merging
* top-k context selection

### 7. Prompt Building

The retrieved context and recent memory are injected into the LLM prompt.

### 8. Answer Generation

Groq LLM generates the final response based on:

* user question
* retrieved document context
* conversation memory

---

## Backend Architecture

The backend follows a layered architecture:

```text
app/
├── api/                 # API routers
│   └── routes/          # Chat, documents, ingestion, memory, feedback, tickets
├── core/                # Config, Redis connection
├── db/                  # Database models, sessions, repositories
├── schemas/             # Request/response schemas
├── services/            # Business logic layer
├── storage/             # MinIO client
├── main.py              # FastAPI app entrypoint
└── mcp_server.py        # MCP server endpoint
```

### Important Services

| Service                  | Responsibility                                     |
| ------------------------ | -------------------------------------------------- |
| `ChatService`            | Main chat orchestration                            |
| `IngestionService`       | Extract, chunk, embed, and store documents         |
| `RetrievalService`       | Hybrid retrieval from vector DB and keyword search |
| `LLMService`             | LLM response generation                            |
| `MemoryService`          | Recent conversation memory with Redis              |
| `PromptBuilderService`   | Builds grounded prompts                            |
| `TicketService`          | Creates tickets from user complaints               |
| `DocumentStorageService` | Handles uploaded documents                         |
| `FeedbackService`        | Stores feedback signals                            |

---

## API Modules

| Route Module       | Purpose                        |
| ------------------ | ------------------------------ |
| `chat.py`          | Chat completion endpoint       |
| `chat_stream.py`   | Streaming chat endpoint        |
| `conversations.py` | Conversation management        |
| `messages.py`      | Message history                |
| `documents.py`     | Document upload and management |
| `ingestion.py`     | Document ingestion             |
| `retrieval.py`     | Retrieval testing/debugging    |
| `memory.py`        | Conversation memory            |
| `feedback.py`      | User feedback                  |
| `tickets.py`       | Ticket management              |
| `health.py`        | Health check                   |

---

## Deployment Architecture

Docker Compose starts the following services:

```text
backend       FastAPI application
frontend      React/Vite application
nginx         Reverse proxy
minio         Object storage
redis         Cache and conversation memory
redisinsight  Redis management UI
```

---

## Getting Started

### Prerequisites

Install:

* Docker
* Docker Compose
* Git

---

## Environment Variables

Create a `.env` file in the root directory.

```env
APP_NAME=FlowAssist Chatbot
APP_VERSION=1.0.0
APP_ENV=local
DEBUG=true
API_PREFIX=/api/v1

# TiDB
TIDB_HOST=your_tidb_host
TIDB_PORT=4000
TIDB_USER=your_tidb_user
TIDB_PASSWORD=your_tidb_password
TIDB_DATABASE=your_database
TIDB_TABLE=rag_embeddings
TIDB_DISTANCE=cosine

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_MEMORY_TTL_SECONDS=3600
REDIS_MAX_MEMORY_MESSAGES=10

# Embedding
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_VECTOR_SIZE=384
EMBEDDING_BATCH_SIZE=32
EMBEDDING_DEVICE=cpu

# Retrieval
RETRIEVAL_TOP_K=8
RETRIEVAL_SCORE_THRESHOLD=0.0

# LLM
LLM_PROVIDER=groq
LLM_MODEL_NAME=llama-3.1-8b-instant
LLM_TEMPERATURE=0.1
LLM_TIMEOUT=60
GROQ_API_KEY=your_groq_api_key

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_SECURE=false
MINIO_RAW_BUCKET_NAME=raw-data
MINIO_PROCESSED_BUCKET_NAME=processed-data

# MinIO root account
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
```

---

## Run with Docker Compose

```bash
docker compose up -d --build
```

After startup:

| Service       | URL                        |
| ------------- | -------------------------- |
| Frontend      | http://localhost           |
| Backend API   | http://localhost:8000      |
| API Docs      | http://localhost:8000/docs |
| MinIO Console | http://localhost:9001      |
| RedisInsight  | http://localhost:5540      |

---

## Run Backend Locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

On Windows PowerShell:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Run Frontend Locally

```bash
cd Frontend
npm install
npm run dev
```

---

## Example Workflow

### 1. Upload a document

Upload an internal document through the frontend or document API.

### 2. Ingest document

The system extracts text, chunks it, generates embeddings, and stores vectors in TiDB.

### 3. Ask a question

Example:

```text
What is the refund policy in the uploaded document?
```

### 4. Retrieve context

The system searches relevant document chunks using hybrid retrieval.

### 5. Generate answer

The LLM answers using the retrieved context and conversation memory.

---

## Retrieval Strategy

FlowAssist uses a hybrid retrieval strategy:

```text
User Query
   ↓
Query Normalization
   ↓
Query Expansion
   ↓
Vector Search + Keyword Search
   ↓
Reciprocal Rank Fusion
   ↓
Top-K Context Selection
   ↓
Prompt Augmentation
   ↓
LLM Answer
```

This improves recall when users ask questions with different phrasing, missing accents, or informal Vietnamese expressions.

---

## Feedback and Ticket Flow

When a user reports that an answer is incorrect, the chatbot can automatically create a ticket containing:

* conversation ID
* user message
* previous assistant answer
* user feedback
* ticket priority

This makes the system closer to an enterprise support assistant rather than a simple demo chatbot.

---

## Project Structure

```text
FlowAssist-Chatbot/
├── Frontend/                 # React/Vite frontend
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── contexts/
│   │   ├── hooks/
│   │   ├── pages/
│   │   └── stores/
│   ├── package.json
│   └── Dockerfile
│
├── app/                      # FastAPI backend
│   ├── api/
│   │   └── routes/
│   ├── core/
│   ├── db/
│   │   └── repositories/
│   ├── schemas/
│   ├── services/
│   ├── storage/
│   ├── main.py
│   └── mcp_server.py
│
├── alembic/                  # Database migrations
├── certs/                    # Database certificates
├── data/                     # Local data directory
├── image/                    # Project images
├── nginx/                    # Nginx config
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
└── README.md
```

---

## What I Built / Learned

This project demonstrates practical backend and AI engineering skills:

* Designed a layered FastAPI backend
* Built an end-to-end RAG pipeline
* Integrated vector search with TiDB
* Implemented hybrid retrieval with keyword fallback
* Used Redis for short-term conversation memory
* Used MinIO for document storage
* Integrated Groq LLM through LangChain
* Built a React frontend for chatbot interaction
* Containerized the full system with Docker Compose
* Added feedback and ticket workflow for enterprise support use cases
* Exposed an MCP-compatible endpoint for future tool integration

---

## Future Improvements

* Add authentication and role-based access control
* Add user workspace and organization support
* Add document-level access permissions
* Add streaming response UI improvements
* Add evaluation metrics for retrieval quality
* Add reranking model for better context selection
* Add observability with Prometheus and Grafana
* Add CI/CD pipeline with GitHub Actions
* Add automated tests for services and APIs
* Add production deployment guide

---

## Author

**FlowAssist Chatbot** was built as a portfolio project to demonstrate backend engineering, AI application development, and production-oriented RAG system design.
