# CodeOrbit AI - Setup Guide (Groq API Version)

## Overview

This version of CodeOrbit AI uses **Groq API with LLaMA 3** for all AI features. Local/offline AI dependencies have been removed to ensure compatibility with macOS Apple Silicon and prevent backend crashes.

## Prerequisites

- Python 3.8 or higher
- Git
- Groq API key (required for AI chat features)

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd CodeOrbit-AI
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Groq API key:

```env
# REQUIRED: Get your API key from https://console.groq.com/keys
GROQ_API_KEY=gsk-your-groq-api-key-here

# Optional: Choose your preferred model
GROQ_MODEL=llama3-70b-8192
# Alternatives: mixtral-8x7b-32768, llama3-8b-8192

# Application Settings (defaults are fine)
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_PORT=8501
```

### 5. Get Groq API Key

1. Go to https://console.groq.com/keys
2. Sign in or create an account (FREE!)
3. Click "Create API Key"
4. Copy the key and paste it in your `.env` file
5. **Note**: Groq offers generous free tier with fast inference

## Running the Application

### Start Backend Server

Open a terminal and run:

```bash
# Activate virtual environment first
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start FastAPI backend
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Start Frontend Dashboard

Open a **new terminal** and run:

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Start Streamlit frontend
streamlit run frontend/app.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`

## Using the Application

### 1. Analyze a Repository

1. Enter a GitHub repository URL (e.g., `https://github.com/fastapi/fastapi`)
2. Specify the branch (default: `main`)
3. Check "Include file content (for AI)" to enable AI features
4. Click "Analyze Repository"

### 2. Use AI Chat Features

Once a repository is analyzed:

1. The system will check if Groq API is configured
2. If configured, you'll see "✅ Groq Connected"
3. Scroll down to the "💬 Ask Your Repository" section
4. Type your question and click "Ask Question"
5. The AI will analyze the repository and provide answers using LLaMA 3

### Example Questions

- "What is the main purpose of this repository?"
- "Where is authentication implemented?"
- "How is the database configured?"
- "What are the main API endpoints?"
- "Explain the project structure"

## Troubleshooting

### Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'groq'`

**Solution**:
```bash
pip install --upgrade groq
```

### Groq API Not Working

**Error**: "Groq API not configured"

**Solution**:
1. Verify `.env` file exists in project root
2. Check `GROQ_API_KEY` is set correctly
3. Restart the backend server
4. Verify API key is valid at https://console.groq.com/keys

**Error**: "Rate limit exceeded"

**Solution**:
1. Groq has generous free tier limits
2. Wait a moment and try again
3. Check usage at https://console.groq.com/

### Frontend Shows "Backend Offline"

**Solution**:
1. Ensure backend is running on port 8000
2. Check terminal for backend errors
3. Try restarting the backend server

### macOS Apple Silicon Issues

This version is specifically designed for macOS Apple Silicon compatibility:
- ✅ No torch/transformers dependencies
- ✅ No FAISS vector database
- ✅ No local model downloads
- ✅ Pure Python with Groq API
- ✅ Fast inference with Groq's infrastructure

## Project Structure

```
CodeOrbit-AI/
├── backend/
│   ├── ai/
│   │   └── chat_service.py      # Groq-based chat service
│   ├── api/
│   │   ├── chat.py               # Chat API endpoints
│   │   └── repository.py         # Repository analysis endpoints
│   ├── core/                     # Core functionality
│   ├── models/                   # Pydantic models
│   └── utils/                    # Utility functions
├── frontend/
│   ├── app.py                    # Streamlit dashboard
│   └── services/
│       └── api.py                # API client
├── shared/
│   ├── config.py                 # Configuration
│   └── logger.py                 # Logging
├── .env                          # Environment variables (create this)
├── .env.example                  # Environment template
├── requirements.txt              # Python dependencies
└── SETUP_GUIDE.md               # This file
```

## Features

### ✅ Working Features

- Repository analysis and parsing
- Technology stack detection
- Code statistics and metrics
- Folder structure visualization
- File content preview
- **AI-powered Q&A using Groq LLaMA 3**
- Repository insights generation
- Suggested questions

### ❌ Removed Features (from offline version)

- Local embeddings generation
- FAISS vector database
- Semantic code search
- Offline AI operation

## Why Groq?

### Advantages over OpenAI

1. **FREE Tier**: Generous free usage limits
2. **Faster**: Groq's LPU™ inference is extremely fast
3. **Open Models**: Uses open-source LLaMA 3
4. **No Billing Required**: Start using immediately
5. **Great for Development**: Perfect for testing and development

### Performance

- **LLaMA 3 70B**: High-quality responses, comparable to GPT-4
- **Inference Speed**: ~300-500 tokens/second (much faster than OpenAI)
- **Context Window**: 8,192 tokens
- **Cost**: FREE for reasonable usage

## Cost Considerations

### Groq API Pricing

- **Free Tier**: Very generous limits for development
- **Typical Usage**: FREE for most use cases
- **No Credit Card Required**: Start immediately

### Typical Usage

- Repository analysis: Free (no API calls)
- Single question: FREE
- 100 questions: FREE (within rate limits)
- 1000+ questions: Still likely FREE

## Support

### Common Issues

1. **"Backend crashes on startup"**
   - This version should NOT crash on macOS
   - Check Python version (3.8+)
   - Verify all dependencies installed

2. **"AI features not working"**
   - Verify Groq API key in `.env`
   - Check Groq console for API status
   - Restart backend after changing `.env`

3. **"Repository analysis fails"**
   - Check repository is public
   - Verify GitHub URL format
   - Try a smaller repository first

### Getting Help

- Check backend terminal for error messages
- Check frontend terminal for connection issues
- Verify `.env` configuration
- Test Groq API key at https://console.groq.com/

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black backend/ frontend/ shared/

# Lint code
flake8 backend/ frontend/ shared/

# Type checking
mypy backend/ frontend/ shared/
```

## Comparison: Groq vs OpenAI

| Feature | Groq (LLaMA 3) | OpenAI (GPT-4) |
|---------|----------------|----------------|
| Cost | FREE | ~$0.01-0.05/query |
| Speed | Very Fast | Moderate |
| Quality | Excellent | Excellent |
| Setup | Immediate | Requires billing |
| Best For | Development, Testing | Production |

## License

See LICENSE file for details.

## Credits

Made with ❤️ by Bob

---

**Note**: This version is optimized for macOS Apple Silicon and uses Groq API for fast, free AI inference with no crashes or compatibility issues.