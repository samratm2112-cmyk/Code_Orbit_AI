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

## Live Demo 
https://codeorbitai-3pgmpb6zbiflsd5zusvblg.streamlit.app/
---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **IBM Bob** - For the amazing AI capabilities
- **lablab.ai** - For organizing the hackathon
- **GroqAI** - For GPT-4 and embeddings
- **FastAPI** - For the excellent framework
- **Streamlit** - For rapid UI development
- **LangChain** - For LLM orchestration

---

## 📧 Contact

- **GitHub Issues:** [Report a bug](https://github.com/samratm2112-cmyk/CodeOrbit_AI/issues)
- **Email:** samratm2105@gmail.com
- 
---

## ⭐ Star Us!

If you find CodeOrbit AI helpful, please give us a star! ⭐

It helps us reach more developers and improve the project.

---

**Made with 🚀 for developers, by developers**

