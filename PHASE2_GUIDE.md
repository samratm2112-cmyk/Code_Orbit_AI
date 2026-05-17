# 🤖 CodeOrbit AI - Phase 2: "Ask My Repository"

## Complete AI Chat Implementation Guide

---

## 🎯 Overview

Phase 2 adds the core AI feature: **intelligent repository question-answering** using:
- **RAG (Retrieval-Augmented Generation)**
- **OpenAI Embeddings**
- **FAISS Vector Search**
- **LangChain Integration**

---

## 📋 What Was Implemented

### 1. **Data Models** (`backend/models/chat.py`)
- `CodeChunk` - Code chunk with metadata
- `ChunkMetadata` - File path, lines, language
- `EmbeddingRequest` - Request to generate embeddings
- `EmbeddingProgress` - Progress tracking
- `ChatQuery` - Question request
- `ChatResponse` - Answer with sources
- `SourceReference` - Code source attribution
- `VectorStoreInfo` - Index information

### 2. **Intelligent Chunking** (`backend/ai/chunker.py`)
- Smart code splitting by structure
- Language-aware chunking
- Preserves file context
- Configurable chunk size (1000 chars) and overlap (200 chars)
- Handles code, markdown, and structured files differently

### 3. **Embeddings Service** (`backend/ai/embeddings.py`)
- OpenAI embeddings integration
- Async batch processing
- Progress tracking
- Rate limiting
- Cost estimation
- Graceful fallback if API key missing

### 4. **FAISS Vector Store** (`backend/ai/vector_store.py`)
- Persistent local storage
- Repository-specific indexes
- Similarity search
- Save/load functionality
- Metadata management

### 5. **Chat Service** (`backend/ai/chat_service.py`)
- RAG-based question answering
- Context retrieval
- LangChain integration
- Source attribution
- Suggested questions

### 6. **Chat API Endpoints** (`backend/api/chat.py`)
- `POST /api/chat/prepare/{repo_id}` - Generate embeddings
- `POST /api/chat/query` - Ask questions
- `GET /api/chat/status/{repo_id}` - Check status
- `GET /api/chat/suggestions/{repo_id}` - Get suggestions
- `DELETE /api/chat/index/{repo_id}` - Delete index
- `GET /api/chat/list` - List all indexes
- `GET /api/chat/health` - Health check

---

## 🚀 Quick Start

### Prerequisites

1. **OpenAI API Key Required**
```bash
# Edit .env file
OPENAI_API_KEY=sk-your-actual-key-here
```

2. **Restart Backend**
```bash
uvicorn backend.main:app --reload
```

3. **Verify AI Features Available**
```bash
curl http://localhost:8000/api/chat/health
```

Expected response:
```json
{
  "status": "healthy",
  "embeddings_service": "available",
  "chat_service": "available"
}
```

---

## 📖 Complete Workflow

### Step 1: Analyze Repository (Phase 1)

```bash
curl -X POST http://localhost:8000/api/repository/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/pallets/flask",
    "branch": "main",
    "include_content": true
  }'
```

**Important:** Set `include_content: true` to enable AI features!

Response includes `repo_id` (e.g., `pallets_flask_abc123`)

### Step 2: Prepare Embeddings

```bash
curl -X POST http://localhost:8000/api/chat/prepare/pallets_flask_abc123
```

This will:
1. Chunk the repository files (✂️)
2. Generate embeddings via OpenAI (🧠)
3. Create FAISS index (📊)
4. Save to disk (💾)

Response:
```json
{
  "success": true,
  "message": "Embeddings generated successfully",
  "info": {
    "repo_id": "pallets_flask_abc123",
    "exists": true,
    "total_vectors": 245,
    "dimension": 1536,
    "created_at": "2024-01-16T12:00:00"
  },
  "statistics": {
    "total_chunks": 245,
    "total_files": 98,
    "languages": {"Python": 200, "JavaScript": 30},
    "avg_chunk_size": 850
  }
}
```

### Step 3: Ask Questions!

```bash
curl -X POST http://localhost:8000/api/chat/query \
  -H "Content-Type: application/json" \
  -d '{
    "repo_id": "pallets_flask_abc123",
    "question": "Where is authentication implemented?",
    "max_results": 5,
    "include_sources": true
  }'
```

Response:
```json
{
  "success": true,
  "answer": "Authentication in Flask is primarily implemented through the session management system...",
  "sources": [
    {
      "file_path": "src/flask/sessions.py",
      "start_line": 45,
      "end_line": 95,
      "relevance_score": 0.92,
      "content_preview": "class SecureCookieSession...",
      "language": "Python"
    }
  ],
  "repo_id": "pallets_flask_abc123",
  "question": "Where is authentication implemented?",
  "processing_time_ms": 1250.5
}
```

---

## 🎯 Example Questions

### General Understanding
```
"What is the main purpose of this repository?"
"What is the project structure?"
"Which files are the entry points?"
```

### Technical Details
```
"Where is authentication implemented?"
"How is the database configured?"
"What testing framework is used?"
"How are environment variables handled?"
```

### Code Navigation
```
"Which files handle routing?"
"Where is error handling implemented?"
"How is logging configured?"
"What are the main API endpoints?"
```

### Architecture
```
"Explain the API flow"
"How is the application structured?"
"What design patterns are used?"
"How do components communicate?"
```

---

## 📊 API Reference

### 1. Prepare Embeddings

**Endpoint:** `POST /api/chat/prepare/{repo_id}`

**Parameters:**
- `repo_id` (path): Repository ID
- `force_regenerate` (query, optional): Force regeneration
- `max_chunks` (query, optional): Limit chunks

**Response:**
```json
{
  "success": true,
  "message": "Embeddings generated successfully",
  "info": {...},
  "statistics": {...}
}
```

**Time:** ~30-60 seconds for small repos, 2-5 minutes for large repos

**Cost:** ~$0.01-0.10 depending on repository size

### 2. Query Repository

**Endpoint:** `POST /api/chat/query`

**Request Body:**
```json
{
  "repo_id": "string",
  "question": "string",
  "max_results": 5,
  "include_sources": true
}
```

**Response:**
```json
{
  "success": true,
  "answer": "string",
  "sources": [...],
  "repo_id": "string",
  "question": "string",
  "processing_time_ms": 1250.5
}
```

**Time:** ~1-3 seconds per query

**Cost:** ~$0.001-0.01 per query

### 3. Check Status

**Endpoint:** `GET /api/chat/status/{repo_id}`

**Response:**
```json
{
  "success": true,
  "info": {
    "repo_id": "string",
    "exists": true,
    "total_vectors": 245,
    "dimension": 1536
  },
  "statistics": {...}
}
```

### 4. Get Suggestions

**Endpoint:** `GET /api/chat/suggestions/{repo_id}`

**Response:**
```json
{
  "success": true,
  "repo_id": "string",
  "suggestions": [
    "What is the main purpose of this repository?",
    "Where is authentication implemented?",
    ...
  ]
}
```

### 5. Delete Index

**Endpoint:** `DELETE /api/chat/index/{repo_id}`

**Response:**
```json
{
  "success": true,
  "message": "Vector index deleted for repository {repo_id}"
}
```

### 6. List Indexes

**Endpoint:** `GET /api/chat/list`

**Response:**
```json
{
  "success": true,
  "total": 3,
  "stores": [...]
}
```

---

## 🐍 Python SDK Usage

### Complete Example

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Step 1: Analyze repository
print("Step 1: Analyzing repository...")
response = requests.post(
    f"{BASE_URL}/api/repository/analyze",
    json={
        "url": "https://github.com/pallets/flask",
        "branch": "main",
        "include_content": True  # Required for AI!
    }
)
data = response.json()
repo_id = data["data"]["metadata"]["repo_id"]
print(f"✓ Repository analyzed: {repo_id}")

# Step 2: Prepare embeddings
print("\nStep 2: Preparing embeddings...")
response = requests.post(
    f"{BASE_URL}/api/chat/prepare/{repo_id}"
)
data = response.json()
print(f"✓ Embeddings created: {data['info']['total_vectors']} vectors")

# Step 3: Ask questions
print("\nStep 3: Asking questions...")
questions = [
    "Where is authentication implemented?",
    "How is routing handled?",
    "What testing framework is used?"
]

for question in questions:
    print(f"\nQ: {question}")
    response = requests.post(
        f"{BASE_URL}/api/chat/query",
        json={
            "repo_id": repo_id,
            "question": question,
            "max_results": 3,
            "include_sources": True
        }
    )
    data = response.json()
    print(f"A: {data['answer'][:200]}...")
    print(f"Sources: {len(data['sources'])} files")
    for source in data['sources'][:2]:
        print(f"  - {source['file_path']} (score: {source['relevance_score']:.2f})")
```

### Async Example

```python
import asyncio
import aiohttp

async def ask_repository(repo_id: str, question: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"http://localhost:8000/api/chat/query",
            json={
                "repo_id": repo_id,
                "question": question
            }
        ) as response:
            return await response.json()

# Usage
answer = asyncio.run(ask_repository(
    "pallets_flask_abc123",
    "Where is authentication implemented?"
))
print(answer["answer"])
```

---

## 🏗️ Architecture

### Data Flow

```
User Question
    ↓
1. Generate Query Embedding (OpenAI)
    ↓
2. Search Vector Store (FAISS)
    ↓
3. Retrieve Top-K Similar Chunks
    ↓
4. Build Context from Chunks
    ↓
5. Generate Answer (LangChain + GPT-4)
    ↓
6. Return Answer + Sources
```

### File Structure

```
backend/
├── ai/
│   ├── __init__.py
│   ├── chunker.py           # Intelligent code chunking
│   ├── embeddings.py        # OpenAI embeddings
│   ├── vector_store.py      # FAISS integration
│   └── chat_service.py      # RAG chat service
├── api/
│   ├── chat.py              # Chat endpoints
│   └── repository.py        # Repository endpoints
└── models/
    ├── chat.py              # Chat models
    └── repository.py        # Repository models

data/
└── vector_stores/
    └── {repo_id}/
        ├── index.faiss      # FAISS index
        ├── metadata.pkl     # Chunk metadata
        └── info.pkl         # Store info
```

---

## 💰 Cost Estimation

### Embeddings Generation
- **Small repo** (50 files): ~$0.01-0.05
- **Medium repo** (200 files): ~$0.05-0.20
- **Large repo** (500+ files): ~$0.20-0.50

### Query Processing
- **Per query**: ~$0.001-0.01
- **100 queries**: ~$0.10-1.00

### Total for Demo
- **3 repositories**: ~$0.50
- **50 queries**: ~$0.50
- **Total**: ~$1.00

---

## 🔧 Configuration

### Chunking Settings

Edit `backend/ai/chunker.py`:
```python
chunker = CodeChunker(
    chunk_size=1000,      # Characters per chunk
    chunk_overlap=200,    # Overlap between chunks
    max_chunk_size=2000   # Maximum chunk size
)
```

### Embedding Settings

Edit `shared/config.py`:
```python
openai_embedding_model = "text-embedding-ada-002"
embedding_dimension = 1536
max_embeddings_per_batch = 100
```

### LLM Settings

Edit `shared/config.py`:
```python
openai_model = "gpt-4"
temperature = 0.7
max_tokens = 4096
```

---

## 🐛 Troubleshooting

### Issue: "Embeddings service not available"

**Solution:**
```bash
# Check .env file
cat .env | grep OPENAI_API_KEY

# Should show:
OPENAI_API_KEY=sk-...

# If not, add it:
echo "OPENAI_API_KEY=sk-your-key" >> .env

# Restart server
uvicorn backend.main:app --reload
```

### Issue: "Vector store not found"

**Solution:**
```bash
# Check if embeddings were generated
curl http://localhost:8000/api/chat/status/{repo_id}

# If not, generate them:
curl -X POST http://localhost:8000/api/chat/prepare/{repo_id}
```

### Issue: "Repository has no file content"

**Solution:**
```bash
# Re-analyze with include_content=true
curl -X POST http://localhost:8000/api/repository/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/user/repo",
    "include_content": true
  }'
```

### Issue: Slow embedding generation

**Solution:**
- Reduce `max_chunks` parameter
- Use smaller repositories for testing
- Check internet connection
- Verify OpenAI API status

### Issue: Poor answer quality

**Solutions:**
1. Increase `max_results` in query (more context)
2. Adjust `chunk_size` (larger chunks = more context)
3. Try different questions (be specific)
4. Check if relevant files were indexed

---

## 📈 Performance Tips

### 1. Optimize Chunking
```python
# For code-heavy repos
chunk_size = 1500  # Larger chunks

# For documentation-heavy repos
chunk_size = 800   # Smaller chunks
```

### 2. Batch Processing
```python
# Process multiple questions
questions = [...]
for q in questions:
    answer = await chat_service.query(...)
```

### 3. Caching
- Vector stores are cached on disk
- Reuse embeddings across sessions
- No need to regenerate unless code changes

### 4. Selective Indexing
```python
# Index only important files
max_chunks = 200  # Limit total chunks
```

---

## ✅ Testing Checklist

- [ ] OpenAI API key configured
- [ ] Backend starts successfully
- [ ] Chat health endpoint returns "healthy"
- [ ] Repository analyzed with `include_content=true`
- [ ] Embeddings generated successfully
- [ ] Vector store exists
- [ ] Query returns relevant answer
- [ ] Sources are attributed correctly
- [ ] Multiple queries work
- [ ] Suggested questions returned

---

## 🎯 Demo Script

### 5-Minute Demo Flow

```bash
# 1. Show repository analysis (30 sec)
curl -X POST .../api/repository/analyze -d '{"url": "..."}'

# 2. Generate embeddings (1 min)
curl -X POST .../api/chat/prepare/{repo_id}

# 3. Ask 3 questions (2 min)
# Q1: "Where is authentication implemented?"
# Q2: "How is routing handled?"
# Q3: "What testing framework is used?"

# 4. Show sources (1 min)
# Highlight file paths and relevance scores

# 5. Show suggested questions (30 sec)
curl .../api/chat/suggestions/{repo_id}
```

---

## 🚀 Next Steps

After Phase 2:
- **Phase 3:** Documentation generation
- **Phase 4:** PR analysis
- **Phase 5:** Code suggestions
- **Phase 6:** Streamlit UI

---

## 📚 Additional Resources

- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [LangChain Documentation](https://python.langchain.com/)
- [RAG Explained](https://www.pinecone.io/learn/retrieval-augmented-generation/)

---

**Made with ❤️ by Bob**

*Phase 2: "Ask My Repository" - Complete!* 🎉