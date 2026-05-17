# CodeOrbit AI - Architecture Document

## 🎯 Project Overview
AI-powered repository intelligence assistant for faster codebase understanding.

## 🏗️ System Architecture

### High-Level Architecture
```
┌─────────────────┐
│   Streamlit UI  │ (Frontend + Simple Backend)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI Server │ (Core Processing Engine)
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌────────┐ ┌──────┐ ┌────────┐ ┌──────────┐
│ GitHub │ │ FAISS│ │LangChain│ │ OpenAI  │
│  API   │ │  DB  │ │ Agents │ │   API   │
└────────┘ └──────┘ └────────┘ └──────────┘
```

## 📁 Folder Structure

```
CodeOrbit_AI/
├── frontend/                    # Streamlit UI
│   ├── app.py                  # Main Streamlit app
│   ├── pages/                  # Multi-page app
│   │   ├── 1_📊_Dashboard.py
│   │   ├── 2_💬_Chat.py
│   │   ├── 3_📝_Documentation.py
│   │   └── 4_🔍_PR_Analysis.py
│   ├── components/             # Reusable UI components
│   │   ├── __init__.py
│   │   ├── sidebar.py
│   │   ├── repo_card.py
│   │   └── chat_interface.py
│   └── utils/                  # Frontend utilities
│       ├── __init__.py
│       └── api_client.py       # FastAPI client wrapper
│
├── backend/                     # FastAPI Server
│   ├── main.py                 # FastAPI app entry point
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   ├── repository.py       # Repo analysis endpoints
│   │   ├── chat.py            # Chat endpoints
│   │   ├── documentation.py   # Doc generation endpoints
│   │   └── pr_analysis.py     # PR analysis endpoints
│   ├── core/                   # Core business logic
│   │   ├── __init__.py
│   │   ├── repo_cloner.py     # GitHub cloning logic
│   │   ├── repo_parser.py     # Code parsing & analysis
│   │   ├── embeddings.py      # Vector embeddings
│   │   └── llm_engine.py      # LangChain orchestration
│   ├── services/               # Service layer
│   │   ├── __init__.py
│   │   ├── analysis_service.py
│   │   ├── chat_service.py
│   │   ├── doc_service.py
│   │   └── pr_service.py
│   ├── models/                 # Pydantic models
│   │   ├── __init__.py
│   │   ├── repository.py
│   │   ├── chat.py
│   │   └── analysis.py
│   └── utils/                  # Backend utilities
│       ├── __init__.py
│       ├── file_parser.py
│       ├── code_analyzer.py
│       └── vector_store.py
│
├── shared/                      # Shared utilities
│   ├── __init__.py
│   ├── config.py               # Configuration management
│   ├── constants.py            # Shared constants
│   └── logger.py               # Logging setup
│
├── data/                        # Data storage
│   ├── repositories/           # Cloned repos (gitignored)
│   ├── vector_stores/          # FAISS indices
│   └── cache/                  # Temporary cache
│
├── tests/                       # Tests (minimal for hackathon)
│   ├── test_api.py
│   └── test_parser.py
│
├── scripts/                     # Utility scripts
│   ├── setup.sh               # Environment setup
│   └── demo_data.py           # Generate demo data
│
├── docs/                        # Documentation
│   ├── API.md                 # API documentation
│   └── DEMO.md                # Demo script
│
├── .env.example                # Environment variables template
├── .gitignore
├── requirements.txt            # Python dependencies
├── README.md                   # Project README
└── ARCHITECTURE.md            # This file
```

## 🔄 Data Flow

### 1. Repository Analysis Flow
```
User Input (GitHub URL)
    ↓
FastAPI: /api/repository/analyze
    ↓
Clone Repository (GitPython)
    ↓
Parse Files (AST, Tree-sitter)
    ↓
Generate Embeddings (OpenAI)
    ↓
Store in FAISS
    ↓
Generate Summary (LangChain + GPT-4)
    ↓
Return Analysis Results
    ↓
Display in Streamlit UI
```

### 2. Chat Flow
```
User Question
    ↓
FastAPI: /api/chat/query
    ↓
Retrieve Context (FAISS similarity search)
    ↓
Build Prompt with Context
    ↓
LangChain Agent (GPT-4)
    ↓
Stream Response
    ↓
Display in Chat Interface
```

### 3. Documentation Generation Flow
```
Repository Analysis Data
    ↓
FastAPI: /api/docs/generate
    ↓
Extract Key Information
    ↓
LangChain Document Chain
    ↓
Generate Markdown
    ↓
Return Documentation
    ↓
Display/Download in UI
```

## 🎯 Feature Priority (MVP First)

### Phase 1: Core MVP (Hours 0-6)
**Priority: CRITICAL**
1. ✅ Basic project structure
2. ✅ GitHub repo cloning
3. ✅ Simple file parsing
4. ✅ Basic embeddings generation
5. ✅ Simple repository summary
6. ✅ Basic Streamlit UI

### Phase 2: Intelligence Layer (Hours 6-9)
**Priority: HIGH**
1. ✅ FAISS vector store integration
2. ✅ LangChain chat functionality
3. ✅ Context-aware Q&A
4. ✅ Architecture visualization

### Phase 3: Advanced Features (Hours 9-12)
**Priority: MEDIUM**
1. ✅ README generation
2. ✅ PR analysis (basic)
3. ✅ Code pattern detection
4. ✅ Onboarding guide generation

### Phase 4: Polish & Demo (Hours 12+)
**Priority: NICE-TO-HAVE**
1. ⚡ UI/UX improvements
2. ⚡ Error handling
3. ⚡ Loading states
4. ⚡ Demo preparation

## 🔌 API Design

### Repository Endpoints
```
POST   /api/repository/analyze
GET    /api/repository/{repo_id}/summary
GET    /api/repository/{repo_id}/structure
GET    /api/repository/{repo_id}/files
DELETE /api/repository/{repo_id}
```

### Chat Endpoints
```
POST   /api/chat/query
GET    /api/chat/{repo_id}/history
POST   /api/chat/{repo_id}/clear
```

### Documentation Endpoints
```
POST   /api/docs/generate-readme
POST   /api/docs/generate-onboarding
GET    /api/docs/{repo_id}/download
```

### PR Analysis Endpoints
```
POST   /api/pr/analyze
GET    /api/pr/{pr_id}/risks
GET    /api/pr/{pr_id}/summary
```

## 📦 Dependencies

### Core Dependencies
```
# Backend
fastapi==0.104.1
uvicorn[standard]==0.24.0
langchain==0.1.0
langchain-openai==0.0.2
faiss-cpu==1.7.4
gitpython==3.1.40
openai==1.3.0
pydantic==2.5.0
python-dotenv==1.0.0

# Frontend
streamlit==1.29.0
requests==2.31.0
plotly==5.18.0

# Utilities
python-multipart==0.0.6
aiofiles==23.2.1
tree-sitter==0.20.4
```

### Optional (if time permits)
```
redis==5.0.1          # Caching
pytest==7.4.3         # Testing
black==23.12.0        # Code formatting
```

## 🚀 Implementation Roadmap (First 12 Hours)

### Hour 0-1: Setup & Foundation
- [ ] Initialize Git repository
- [ ] Create folder structure
- [ ] Setup virtual environment
- [ ] Install dependencies
- [ ] Configure environment variables
- [ ] Create basic FastAPI app
- [ ] Create basic Streamlit app

### Hour 1-2: Repository Cloning
- [ ] Implement GitPython cloning logic
- [ ] Add error handling for invalid URLs
- [ ] Create temporary storage system
- [ ] Test with sample repositories

### Hour 2-4: File Parsing & Analysis
- [ ] Implement file tree traversal
- [ ] Parse common file types (py, js, java, etc.)
- [ ] Extract code structure (functions, classes)
- [ ] Generate basic statistics
- [ ] Create repository metadata model

### Hour 4-6: Embeddings & Vector Store
- [ ] Setup OpenAI embeddings
- [ ] Chunk code files intelligently
- [ ] Create FAISS index
- [ ] Implement similarity search
- [ ] Test retrieval quality

### Hour 6-8: LangChain Integration
- [ ] Setup LangChain with GPT-4
- [ ] Create prompt templates
- [ ] Implement repository summarization
- [ ] Build Q&A chain with context
- [ ] Test response quality

### Hour 8-10: Streamlit UI
- [ ] Create main dashboard
- [ ] Add repository input form
- [ ] Display analysis results
- [ ] Build chat interface
- [ ] Add loading states

### Hour 10-12: Documentation Generation
- [ ] Implement README generator
- [ ] Create onboarding guide template
- [ ] Add download functionality
- [ ] Polish UI components

## 💡 Optimization Tips

### Speed Optimizations
1. **Parallel Processing**: Use asyncio for concurrent operations
2. **Caching**: Cache embeddings and summaries
3. **Lazy Loading**: Load files on-demand
4. **Batch Processing**: Process multiple files together

### Cost Optimizations (40 Bobcoins)
1. **Smart Chunking**: Reduce token usage
2. **Caching**: Avoid redundant API calls
3. **Selective Analysis**: Focus on important files
4. **Streaming**: Use streaming responses

### Demo Optimizations
1. **Pre-analyzed Repos**: Have 2-3 repos ready
2. **Fast Mode**: Skip heavy analysis for demo
3. **Mock Data**: Use cached responses
4. **Error Recovery**: Graceful fallbacks

## 🎨 UI/UX Considerations

### Key Screens
1. **Landing Page**: Simple URL input + examples
2. **Analysis Dashboard**: Visual repo overview
3. **Chat Interface**: Clean, responsive chat
4. **Documentation Viewer**: Markdown preview

### Design Principles
- Minimal clicks to value
- Clear loading indicators
- Informative error messages
- Mobile-friendly (bonus)

## 🔒 Security Considerations

1. **API Keys**: Use environment variables
2. **Rate Limiting**: Prevent abuse
3. **Input Validation**: Sanitize GitHub URLs
4. **Temporary Storage**: Auto-cleanup cloned repos
5. **CORS**: Configure properly for deployment

## 📊 Success Metrics

### Technical Metrics
- Repository analysis time < 2 minutes
- Chat response time < 5 seconds
- Support for 5+ programming languages
- 90%+ uptime during demo

### Demo Metrics
- Analyze 3 different repositories
- Answer 10+ questions accurately
- Generate complete README
- Identify code patterns

## 🎯 Hackathon Strategy

### Do's ✅
- Focus on working features
- Use pre-built components
- Prioritize demo polish
- Test with real repositories
- Document as you go

### Don'ts ❌
- Don't build authentication (yet)
- Don't optimize prematurely
- Don't add unnecessary features
- Don't over-engineer
- Don't skip testing

## 🚢 Deployment Plan

### Streamlit Cloud (Frontend)
- One-click deployment
- Free tier sufficient
- Auto-updates from Git

### Render (Backend)
- Free tier for FastAPI
- Environment variables
- Auto-deploy from Git

### Environment Variables
```
OPENAI_API_KEY=your_key
GITHUB_TOKEN=optional
FAISS_INDEX_PATH=./data/vector_stores
REPO_STORAGE_PATH=./data/repositories
```

## 📝 Next Steps

After architecture approval:
1. Create folder structure
2. Setup development environment
3. Implement core cloning logic
4. Build basic API endpoints
5. Create simple UI
6. Integrate AI components
7. Test and iterate
8. Polish for demo

---

**Remember**: Ship working features over perfect code. Demo quality > Code quality for hackathons.