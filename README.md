# 🚀 CodeOrbit AI

> **AI-Powered Repository Intelligence Assistant**  
> Understand any GitHub repository in minutes, not hours.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Built for the **IBM Bob × lablab.ai Hackathon** 🏆

---

## 🎯 Problem Statement

Developers waste countless hours:
- 📚 Understanding unfamiliar codebases
- 🔍 Searching for specific functionality
- 📝 Writing documentation
- 👥 Onboarding new team members
- 🔎 Reviewing pull requests

**Existing AI coding assistants generate code but lack deep repository understanding.**

---

## 💡 Our Solution

CodeOrbit AI is an intelligent assistant that:

✅ **Analyzes** any GitHub repository in minutes  
✅ **Explains** architecture and code structure  
✅ **Answers** questions about the codebase  
✅ **Generates** documentation automatically  
✅ **Reviews** pull requests for risks  
✅ **Guides** new developers through onboarding  

---

## ✨ Key Features

### 🔍 Repository Analysis
- Clone and parse any public GitHub repository
- Extract code structure, dependencies, and patterns
- Identify entry points and key files
- Generate comprehensive statistics

### 💬 Intelligent Chat
- Ask questions about the codebase in natural language
- Get context-aware answers with code examples
- Retrieve relevant code snippets automatically
- Maintain conversation history

### 📝 Documentation Generation
- Auto-generate README files
- Create onboarding guides for new developers
- Generate API documentation
- Export in multiple formats (Markdown, PDF, HTML)

### 🔎 PR Analysis (Coming Soon)
- Analyze pull requests for potential issues
- Detect security vulnerabilities
- Identify performance bottlenecks
- Suggest improvements

---

## 🏗️ Architecture

```
┌─────────────────┐
│   Streamlit UI  │ ← User Interface
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI Server │ ← Core Processing
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌────────┐ ┌──────┐ ┌────────┐ ┌──────────┐
│ GitHub │ │ FAISS│ │LangChain│ │ OpenAI  │
│  API   │ │  DB  │ │ Agents │ │   API   │
└────────┘ └──────┘ └────────┘ └──────────┘
```

### Tech Stack

**Frontend:**
- 🎨 Streamlit - Interactive web interface
- 📊 Plotly - Data visualization

**Backend:**
- ⚡ FastAPI - High-performance API server
- 🐍 Python 3.9+ - Core language

**AI & ML:**
- 🤖 LangChain - LLM orchestration
- 🧠 OpenAI GPT-4 - Language model
- 📚 FAISS - Vector similarity search
- 🔤 OpenAI Embeddings - Text embeddings

**Repository Management:**
- 📦 GitPython - Git operations
- 🌳 Tree-sitter - Code parsing

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- OpenAI API key
- Git installed

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/CodeOrbit_AI.git
cd CodeOrbit_AI
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_key_here
```

5. **Run the application**

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
streamlit run app.py
```

6. **Open your browser**
```
http://localhost:8501
```

---

## 📖 Usage

### 1. Analyze a Repository

1. Enter a GitHub repository URL
2. Click "Analyze Repository"
3. Wait for analysis to complete (1-3 minutes)
4. View comprehensive summary and statistics

### 2. Chat with Your Repository

1. Navigate to the Chat page
2. Ask questions about the codebase
3. Get instant, context-aware answers
4. View relevant code snippets

### 3. Generate Documentation

1. Go to the Documentation page
2. Select document type (README, Onboarding, etc.)
3. Click "Generate"
4. Preview and download

---

## 📁 Project Structure

```
CodeOrbit_AI/
├── frontend/              # Streamlit UI
│   ├── app.py            # Main application
│   ├── pages/            # Multi-page app
│   ├── components/       # Reusable components
│   └── utils/            # Frontend utilities
│
├── backend/              # FastAPI server
│   ├── main.py          # API entry point
│   ├── api/             # API routes
│   ├── core/            # Core logic
│   ├── services/        # Business logic
│   ├── models/          # Data models
│   └── utils/           # Backend utilities
│
├── shared/              # Shared code
│   ├── config.py        # Configuration
│   ├── constants.py     # Constants
│   └── logger.py        # Logging
│
├── data/                # Data storage
│   ├── repositories/    # Cloned repos
│   ├── vector_stores/   # FAISS indices
│   └── cache/           # Temporary cache
│
├── docs/                # Documentation
│   ├── API.md          # API documentation
│   └── ARCHITECTURE.md # Architecture details
│
└── tests/              # Tests
```

---

## 🔧 Configuration

Key configuration options in `.env`:

```bash
# OpenAI
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4

# Storage
REPO_STORAGE_PATH=./data/repositories
VECTOR_STORE_PATH=./data/vector_stores

# Analysis
MAX_FILE_SIZE_MB=5
MAX_REPO_SIZE_MB=500

# Chat
MAX_CONTEXT_CHUNKS=5
STREAMING_ENABLED=True
```

See `.env.example` for all options.

---

## 📊 API Documentation

Full API documentation available at:
- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Markdown:** [docs/API.md](docs/API.md)

### Quick API Example

```python
import requests

# Analyze repository
response = requests.post(
    "http://localhost:8000/api/repository/analyze",
    json={"url": "https://github.com/fastapi/fastapi"}
)
repo_data = response.json()

# Ask a question
response = requests.post(
    "http://localhost:8000/api/chat/query",
    json={
        "repo_id": repo_data["data"]["repo_id"],
        "question": "How does routing work?"
    }
)
answer = response.json()
```

---

## 🎯 Roadmap

### Phase 1: MVP (Current) ✅
- [x] Repository cloning and parsing
- [x] Basic code analysis
- [x] Vector embeddings and search
- [x] Chat functionality
- [x] Documentation generation
- [x] Streamlit UI

### Phase 2: Enhancement 🚧
- [ ] PR analysis and risk detection
- [ ] Multi-repository support
- [ ] Code search functionality
- [ ] Architecture visualization
- [ ] Export to multiple formats

### Phase 3: Advanced Features 🔮
- [ ] Real-time collaboration
- [ ] Custom AI models
- [ ] IDE integrations
- [ ] Team analytics
- [ ] Private repository support

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
pytest

# Format code
black .

# Lint code
flake8
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue:** OpenAI API rate limit exceeded  
**Solution:** Reduce `MAX_EMBEDDINGS_PER_BATCH` in `.env`

**Issue:** Repository too large  
**Solution:** Increase `MAX_REPO_SIZE_MB` or analyze specific directories

**Issue:** FAISS index not found  
**Solution:** Delete `data/vector_stores` and re-analyze repository

**Issue:** Streamlit connection error  
**Solution:** Ensure backend is running on port 8000

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

Built with ❤️ by Team CodeOrbit for IBM Bob × lablab.ai Hackathon

- **Developer 1** - Backend & AI
- **Developer 2** - Frontend & UX
- **Developer 3** - Integration & Testing

---

## 🙏 Acknowledgments

- **IBM Bob** - For the amazing AI capabilities
- **lablab.ai** - For organizing the hackathon
- **OpenAI** - For GPT-4 and embeddings
- **FastAPI** - For the excellent framework
- **Streamlit** - For rapid UI development
- **LangChain** - For LLM orchestration

---

## 📧 Contact

- **GitHub Issues:** [Report a bug](https://github.com/yourusername/CodeOrbit_AI/issues)
- **Email:** team@codeorbit.ai
- **Twitter:** [@CodeOrbitAI](https://twitter.com/CodeOrbitAI)

---

## ⭐ Star Us!

If you find CodeOrbit AI helpful, please give us a star! ⭐

It helps us reach more developers and improve the project.

---

<div align="center">

**Made with 🚀 for developers, by developers**

[Website](https://codeorbit.ai) • [Documentation](docs/) • [API](docs/API.md) • [Demo](https://demo.codeorbit.ai)

</div>