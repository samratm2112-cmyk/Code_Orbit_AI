# CodeOrbit AI - Usage Guide
## Repository Ingestion Pipeline

This guide covers the first phase of CodeOrbit AI: the repository ingestion and intelligence pipeline.

---

## 📋 Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [API Usage](#api-usage)
4. [Python SDK Usage](#python-sdk-usage)
5. [Example Outputs](#example-outputs)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Installation

### Prerequisites

- Python 3.9+
- Git installed
- OpenAI API key (for future AI features)

### Setup Steps

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd CodeOrbit_AI

# 2. Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add your OpenAI API key

# 5. Verify installation
python -c "from backend.core.repo_parser import RepositoryParser; print('✅ Installation successful!')"
```

---

## ⚡ Quick Start

### Option 1: Using the API Server

```bash
# Start the FastAPI server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Server will be available at:
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs
# - Health: http://localhost:8000/health
```

### Option 2: Using Python Directly

```python
import asyncio
from backend.core.repo_parser import RepositoryParser

async def analyze_repo():
    parser = RepositoryParser()
    
    # Analyze a repository
    analysis = await parser.parse_repository(
        url="https://github.com/pallets/flask",
        branch="main",
        include_content=True
    )
    
    # Print summary
    print(f"Repository: {analysis.metadata.name}")
    print(f"Total Files: {analysis.statistics.total_files}")
    print(f"Languages: {analysis.technology_stack.languages}")
    
    return analysis

# Run
analysis = asyncio.run(analyze_repo())
```

---

## 🔌 API Usage

### 1. Analyze Repository

**Endpoint:** `POST /api/repository/analyze`

**Request:**
```json
{
  "url": "https://github.com/fastapi/fastapi",
  "branch": "master",
  "include_content": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Repository analyzed successfully",
  "data": {
    "metadata": {
      "repo_id": "fastapi_fastapi_abc123",
      "name": "fastapi",
      "owner": "fastapi",
      "url": "https://github.com/fastapi/fastapi",
      "branch": "master",
      "status": "completed"
    },
    "statistics": {
      "total_files": 245,
      "total_source_files": 180,
      "total_lines": 15420,
      "total_size_bytes": 2048576
    },
    "technology_stack": {
      "languages": ["Python", "JavaScript"],
      "frameworks": ["FastAPI", "Pydantic"],
      "tools": ["Docker", "Git", "pytest"]
    },
    "folder_structure": "fastapi/\n├── fastapi/\n├── tests/\n...",
    "important_files": ["README.md", "setup.py", "pyproject.toml"],
    "entry_points": ["main.py"]
  }
}
```

### 2. Get Repository Summary

**Endpoint:** `GET /api/repository/{repo_id}/summary`

**Example:**
```bash
curl http://localhost:8000/api/repository/fastapi_fastapi_abc123/summary
```

### 3. Get Repository Structure

**Endpoint:** `GET /api/repository/{repo_id}/structure`

### 4. Get Repository Statistics

**Endpoint:** `GET /api/repository/{repo_id}/statistics`

### 5. List All Repositories

**Endpoint:** `GET /api/repository/list`

### 6. Delete Repository

**Endpoint:** `DELETE /api/repository/{repo_id}`

---

## 🐍 Python SDK Usage

### Basic Analysis

```python
from backend.core.repo_parser import RepositoryParser
import asyncio

async def main():
    parser = RepositoryParser()
    
    # Analyze repository
    analysis = await parser.parse_repository(
        url="https://github.com/pallets/flask",
        branch="main",
        include_content=False  # Set to True to include file contents
    )
    
    # Access results
    print(f"Repository: {analysis.metadata.name}")
    print(f"Owner: {analysis.metadata.owner}")
    print(f"Total Files: {analysis.statistics.total_files}")
    print(f"Languages: {analysis.technology_stack.languages}")
    
    # Get summary
    summary = parser.get_repository_summary(analysis)
    print(summary)
    
    # Cleanup
    parser.cleanup_repository(analysis.metadata.repo_id)

asyncio.run(main())
```

### Advanced Usage

```python
from backend.core.repo_parser import RepositoryParser
from backend.utils.repo_analyzer import RepositoryAnalyzer
import asyncio

async def advanced_analysis():
    parser = RepositoryParser()
    analyzer = RepositoryAnalyzer()
    
    # Analyze with content
    analysis = await parser.parse_repository(
        url="https://github.com/streamlit/streamlit",
        branch="develop",
        include_content=True
    )
    
    # Calculate complexity
    complexity = analyzer.calculate_complexity_score(analysis.statistics)
    print(f"Complexity Level: {complexity['level']}")
    print(f"Complexity Score: {complexity['score']}")
    
    # Prepare for embeddings
    documents = parser.prepare_for_embeddings(analysis, max_files=100)
    print(f"Documents for embeddings: {len(documents)}")
    
    # Generate summary text
    summary_text = analyzer.generate_summary_text(
        analysis.statistics,
        analysis.technology_stack
    )
    print(summary_text)
    
    return analysis

asyncio.run(advanced_analysis())
```

### Component-Level Usage

```python
# Use individual components

# 1. Clone Repository
from backend.core.repo_cloner import RepositoryCloner

cloner = RepositoryCloner()
metadata = cloner.clone_repository("https://github.com/pallets/flask")
print(f"Cloned to: {metadata.clone_path}")

# 2. Parse Files
from backend.utils.file_parser import FileParser
from pathlib import Path

parser = FileParser()
files = parser.parse_directory(Path(metadata.clone_path))
print(f"Parsed {len(files)} files")

# 3. Detect Technology
from backend.utils.tech_detector import TechnologyDetector

detector = TechnologyDetector()
tech_stack = detector.detect_from_files(Path(metadata.clone_path))
print(f"Technologies: {tech_stack.frameworks}")

# 4. Generate Statistics
from backend.utils.repo_analyzer import RepositoryAnalyzer

analyzer = RepositoryAnalyzer()
stats = analyzer.analyze(files)
print(f"Total lines: {stats.total_lines}")

# 5. Generate Folder Tree
from backend.utils.folder_tree import FolderTreeGenerator

tree_gen = FolderTreeGenerator()
tree = tree_gen.generate_compact_tree(Path(metadata.clone_path))
print(tree)
```

---

## 📊 Example Outputs

### Repository Analysis Output

```
Repository: flask
Owner: pallets
Repo ID: pallets_flask_20240116123456_abc12345

Statistics:
  Total Files: 156
  Source Files: 98
  Total Lines: 12,450
  Size: 1.85 MB

Languages:
  - Python: 98 files
  - JavaScript: 12 files
  - HTML: 25 files
  - CSS: 8 files

Technology Stack:
  Languages: Python, JavaScript, HTML, CSS
  Frameworks: Flask, Jinja2
  Tools: Docker, Git, pytest, tox

Important Files (10):
  - README.md
  - setup.py
  - requirements.txt
  - CONTRIBUTING.md
  - LICENSE
  - pyproject.toml
  - tox.ini
  - .github/workflows/tests.yaml
  - docs/conf.py
  - examples/tutorial/flaskr/__init__.py

Entry Points (3):
  - src/flask/__init__.py
  - src/flask/app.py
  - examples/tutorial/flaskr/__init__.py

Folder Structure (preview):
flask/
├── src/
│   └── flask/
│       ├── __init__.py
│       ├── app.py
│       ├── blueprints.py
│       └── ...
├── tests/
├── docs/
├── examples/
└── requirements/
```

### JSON Output Structure

```json
{
  "metadata": {
    "repo_id": "pallets_flask_abc123",
    "name": "flask",
    "owner": "pallets",
    "url": "https://github.com/pallets/flask",
    "branch": "main",
    "clone_path": "/data/repositories/pallets_flask_abc123",
    "created_at": "2024-01-16T12:34:56.789Z",
    "status": "completed"
  },
  "statistics": {
    "total_files": 156,
    "total_source_files": 98,
    "total_lines": 12450,
    "total_size_bytes": 1940000,
    "languages_distribution": {
      "Python": 98,
      "JavaScript": 12,
      "HTML": 25,
      "CSS": 8
    },
    "file_type_distribution": {
      ".py": 98,
      ".js": 12,
      ".html": 25,
      ".css": 8,
      ".md": 10
    },
    "largest_files": [
      {
        "path": "src/flask/app.py",
        "size_bytes": 45000,
        "size_kb": 43.95,
        "lines": 1250,
        "language": "Python"
      }
    ]
  },
  "technology_stack": {
    "languages": ["Python", "JavaScript", "HTML", "CSS"],
    "frameworks": ["Flask", "Jinja2"],
    "tools": ["Docker", "Git", "pytest", "tox"],
    "databases": []
  },
  "folder_structure": "...",
  "important_files": ["README.md", "setup.py", ...],
  "entry_points": ["src/flask/__init__.py", ...]
}
```

---

## 🧪 Testing

### Run Test Suite

```bash
# Run all tests
python tests/test_repository_pipeline.py

# Expected output:
# ============================================================
# REPOSITORY INGESTION PIPELINE - TEST SUITE
# ============================================================
# 
# TEST 1: Small Repository (Flask)
# ✅ Test 1 PASSED
# 
# TEST 2: Medium Repository (FastAPI)
# ✅ Test 2 PASSED
# 
# TEST 3: Repository with Content Extraction
# ✅ Test 3 PASSED
# 
# TEST 4: Error Handling
# ✅ Test 4 PASSED
# 
# 🎉 ALL TESTS PASSED!
```

### Manual Testing with curl

```bash
# Start server
uvicorn backend.main:app --reload

# Test analyze endpoint
curl -X POST http://localhost:8000/api/repository/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/pallets/flask",
    "branch": "main",
    "include_content": false
  }'

# Test get summary
curl http://localhost:8000/api/repository/{repo_id}/summary

# Test list repositories
curl http://localhost:8000/api/repository/list
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Import Errors

**Problem:** `ModuleNotFoundError: No module named 'shared'`

**Solution:**
```bash
# Make sure you're in the project root
cd CodeOrbit_AI

# Reinstall dependencies
pip install -r requirements.txt

# Run from project root
python -m tests.test_repository_pipeline
```

#### 2. Git Clone Fails

**Problem:** `Repository not found or is private`

**Solution:**
- Verify the URL is correct
- Ensure the repository is public
- Check your internet connection
- For private repos, add GitHub token to `.env`:
  ```
  GITHUB_TOKEN=your_github_token
  ```

#### 3. Large Repository Timeout

**Problem:** Analysis takes too long or times out

**Solution:**
```python
# Analyze without content for faster processing
analysis = await parser.parse_repository(
    url="https://github.com/large/repo",
    include_content=False  # Much faster
)
```

#### 4. Encoding Errors

**Problem:** `UnicodeDecodeError` when reading files

**Solution:** The file parser automatically handles encoding issues. If problems persist:
```python
# The parser tries multiple encodings automatically
# Check logs for which files failed
```

#### 5. Disk Space Issues

**Problem:** Running out of disk space

**Solution:**
```python
# Clean up old repositories
parser.cleanup_repository(repo_id)

# Or clean all
import shutil
shutil.rmtree('data/repositories')
```

---

## 📝 Configuration

### Environment Variables

Edit `.env` file:

```bash
# Application
APP_NAME=CodeOrbit AI
DEBUG=True
LOG_LEVEL=INFO

# OpenAI (for future features)
OPENAI_API_KEY=your_key_here

# GitHub (optional, for private repos)
GITHUB_TOKEN=

# Storage
REPO_STORAGE_PATH=./data/repositories
VECTOR_STORE_PATH=./data/vector_stores
CACHE_PATH=./data/cache

# Analysis Settings
MAX_FILE_SIZE_MB=5
MAX_REPO_SIZE_MB=500
SUPPORTED_EXTENSIONS=.py,.js,.jsx,.ts,.tsx,.java,.go,.rs,.cpp,.c,.h,.md,.json,.yaml,.yml
```

---

## 🎯 Next Steps

After completing Phase 1 (Repository Ingestion), the next phases will add:

- **Phase 2:** Vector embeddings and FAISS integration
- **Phase 3:** LangChain-powered chat interface
- **Phase 4:** Documentation generation
- **Phase 5:** PR analysis

Stay tuned for updates!

---

## 📚 Additional Resources

- [Architecture Documentation](ARCHITECTURE.md)
- [Implementation Roadmap](IMPLEMENTATION_ROADMAP.md)
- [API Documentation](docs/API.md)
- [Demo Guide](docs/DEMO.md)

---

**Made with ❤️ by Bob**