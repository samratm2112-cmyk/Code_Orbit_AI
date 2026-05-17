# 🚀 CodeOrbit AI - Startup Guide

## Configuration Fix Applied ✅

The backend has been fixed to work **without requiring an OpenAI API key** during Phase 1 development.

---

## 📋 What Was Fixed

### 1. **Configuration System** (`shared/config.py`)
- ✅ Made `openai_api_key` **Optional** (not required)
- ✅ Added `validate_openai_config()` method
- ✅ Added `require_openai()` method for AI features
- ✅ Updated to Pydantic v2 syntax (`model_config`)
- ✅ Added startup logging for configuration status

### 2. **Environment Files**
- ✅ Updated `.env.example` with clear comments
- ✅ Created `.env` file with development defaults
- ✅ OpenAI key is commented out by default

### 3. **Backend Startup** (`backend/main.py`)
- ✅ Enhanced startup logging
- ✅ Shows configuration status
- ✅ Warns if OpenAI is not configured (but doesn't fail)
- ✅ Clear success message when ready

---

## 🎯 Quick Start

### Step 1: Verify Environment File

Your `.env` file should look like this:

```bash
# CodeOrbit AI - Development Environment

# Application Settings
DEBUG=True
LOG_LEVEL=INFO

# OpenAI Configuration (Optional - only needed for Phase 2+ AI features)
# Uncomment and add your key when ready for AI features:
# OPENAI_API_KEY=your_key_here

# GitHub Token (Optional - for private repos)
# GITHUB_TOKEN=
```

### Step 2: Start the Backend

```bash
# Make sure you're in the project root
cd c:/Users/Admin/Documents/CodeOrbit_AI

# Activate virtual environment (if using one)
# venv\Scripts\activate

# Start the FastAPI server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Expected Successful Output

You should see:

```
INFO:     Will watch for changes in these directories: ['c:\\Users\\Admin\\Documents\\CodeOrbit_AI']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
2024-01-16 12:34:56 | INFO     | shared.config:<module>:153 - Configuration loaded: CodeOrbit AI v1.0.0
2024-01-16 12:34:56 | INFO     | shared.config:<module>:154 - Debug mode: True
2024-01-16 12:34:56 | INFO     | shared.config:<module>:155 - Storage path: c:\Users\Admin\Documents\CodeOrbit_AI\data\repositories
2024-01-16 12:34:56 | WARNING  | shared.config:<module>:160 - ⚠ OpenAI API key not configured (AI features will be disabled)
2024-01-16 12:34:56 | INFO     | backend.main:startup_event:62 - ============================================================
2024-01-16 12:34:56 | INFO     | backend.main:startup_event:63 - 🚀 Starting CodeOrbit AI v1.0.0
2024-01-16 12:34:56 | INFO     | backend.main:startup_event:64 - ============================================================
2024-01-16 12:34:56 | INFO     | backend.main:startup_event:65 - Debug mode: True
2024-01-16 12:34:56 | INFO     | backend.main:startup_event:66 - Log level: INFO
2024-01-16 12:34:56 | INFO     | backend.main:startup_event:67 - Storage path: c:\Users\Admin\Documents\CodeOrbit_AI\data\repositories
2024-01-16 12:34:56 | INFO     | backend.main:startup_event:71 - ✓ All directories verified
2024-01-16 12:34:56 | WARNING  | backend.main:startup_event:77 - ⚠ OpenAI API key not configured
2024-01-16 12:34:56 | WARNING  | backend.main:startup_event:78 -   Phase 1 (Repository Ingestion) will work normally
2024-01-16 12:34:56 | WARNING  | backend.main:startup_event:79 -   Phase 2+ (AI features) will require API key
2024-01-16 12:34:56 | INFO     | backend.main:startup_event:81 - ============================================================
2024-01-16 12:34:56 | SUCCESS  | backend.main:startup_event:82 - ✅ CodeOrbit AI is ready!
2024-01-16 12:34:56 | INFO     | backend.main:startup_event:83 - 📚 API Documentation: http://0.0.0.0:8000/docs
2024-01-16 12:34:56 | INFO     | backend.main:startup_event:84 - ============================================================
INFO:     Application startup complete.
```

**Key Points:**
- ⚠️ Warnings about OpenAI are **NORMAL** and **EXPECTED**
- ✅ The server starts successfully
- 🎯 Phase 1 features work without OpenAI

---

## 🧪 Test the Backend

### Option 1: Browser
Open: http://localhost:8000/docs

### Option 2: curl
```bash
# Health check
curl http://localhost:8000/health

# Repository health
curl http://localhost:8000/api/repository/health

# Analyze a repository (this works without OpenAI!)
curl -X POST http://localhost:8000/api/repository/analyze \
  -H "Content-Type: application/json" \
  -d "{\"url\": \"https://github.com/pallets/flask\", \"branch\": \"main\", \"include_content\": false}"
```

### Option 3: Python
```python
import requests

# Test health
response = requests.get("http://localhost:8000/health")
print(response.json())

# Analyze repository
response = requests.post(
    "http://localhost:8000/api/repository/analyze",
    json={
        "url": "https://github.com/pallets/flask",
        "branch": "main",
        "include_content": False
    }
)
print(response.json())
```

---

## 🔧 Configuration Details

### How It Works Now

1. **Without OpenAI Key:**
   - ✅ Backend starts successfully
   - ✅ Repository cloning works
   - ✅ File parsing works
   - ✅ Technology detection works
   - ✅ Statistics generation works
   - ✅ All Phase 1 features work
   - ⚠️ Warning logged (but not an error)

2. **With OpenAI Key (Future):**
   - ✅ All Phase 1 features work
   - ✅ Embeddings generation (Phase 2)
   - ✅ AI chat (Phase 2)
   - ✅ Documentation generation (Phase 3)

### Adding OpenAI Key Later

When you're ready for AI features:

1. Edit `.env`:
```bash
# Uncomment and add your key:
OPENAI_API_KEY=sk-your-actual-key-here
```

2. Restart the server:
```bash
# Press CTRL+C to stop
# Then restart:
uvicorn backend.main:app --reload
```

3. You'll see:
```
✓ OpenAI API key configured (AI features available)
```

---

## 🐛 Troubleshooting

### Issue: "Field required" error for openai_api_key

**Solution:** You're using old code. The fix has been applied:
- `shared/config.py` line 29: `openai_api_key: Optional[str] = None`

### Issue: Import errors

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or specific packages:
pip install pydantic==2.5.0 pydantic-settings==2.1.0
```

### Issue: Module not found

**Solution:**
```bash
# Make sure you're in project root
cd c:/Users/Admin/Documents/CodeOrbit_AI

# Run from project root
python -m backend.main
# OR
uvicorn backend.main:app --reload
```

### Issue: Port already in use

**Solution:**
```bash
# Use a different port
uvicorn backend.main:app --reload --port 8001

# Or kill the process using port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <process_id> /F
```

---

## 📊 What Works Without OpenAI

### ✅ Fully Functional (Phase 1)

1. **Repository Cloning**
   - Clone any public GitHub repository
   - URL validation
   - Error handling

2. **File Parsing**
   - Parse 20+ file types
   - Extract metadata
   - Handle encoding issues

3. **Technology Detection**
   - Detect 15+ frameworks
   - Identify languages
   - Parse package files

4. **Statistics Generation**
   - File counts
   - Language distribution
   - Complexity analysis

5. **Folder Tree**
   - Visual hierarchy
   - Clean formatting

6. **API Endpoints**
   - All repository endpoints work
   - Full REST API
   - Swagger documentation

### ⏳ Requires OpenAI (Phase 2+)

1. **Embeddings Generation**
   - Will call `settings.require_openai()`
   - Clear error message if not configured

2. **AI Chat**
   - Will call `settings.require_openai()`
   - Clear error message if not configured

3. **Documentation Generation**
   - Will call `settings.require_openai()`
   - Clear error message if not configured

---

## 🎯 Development Workflow

### Phase 1 (Current - No OpenAI Needed)
```bash
# 1. Start backend
uvicorn backend.main:app --reload

# 2. Test repository ingestion
curl -X POST http://localhost:8000/api/repository/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/pallets/flask"}'

# 3. Develop and test features
# All Phase 1 features work!
```

### Phase 2 (Future - OpenAI Required)
```bash
# 1. Add OpenAI key to .env
# OPENAI_API_KEY=sk-...

# 2. Restart backend
uvicorn backend.main:app --reload

# 3. Test AI features
# Embeddings, chat, etc. will now work
```

---

## 📝 Summary of Changes

### Files Modified:

1. **`shared/config.py`**
   - Made `openai_api_key` optional
   - Added validation methods
   - Updated to Pydantic v2
   - Added configuration logging

2. **`.env.example`**
   - Added clear comments
   - Made OpenAI optional

3. **`backend/main.py`**
   - Enhanced startup logging
   - Added configuration status display

4. **`.env`** (created)
   - Development defaults
   - OpenAI commented out

### Key Changes:

```python
# BEFORE (caused error):
openai_api_key: str  # Required!

# AFTER (works without key):
openai_api_key: Optional[str] = None  # Optional!
```

---

## ✅ Verification Checklist

- [ ] `.env` file exists in project root
- [ ] `openai_api_key` is optional in `shared/config.py`
- [ ] Backend starts without errors
- [ ] Warning about OpenAI appears (this is normal!)
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Health endpoint returns 200
- [ ] Repository analysis works

---

## 🚀 Next Steps

1. **Start the backend** (should work now!)
2. **Test Phase 1 features** (repository ingestion)
3. **Develop Phase 2** (when ready, add OpenAI key)
4. **Deploy** (environment variables work the same way)

---

**Made with ❤️ by Bob**

*Configuration fixed for hackathon-friendly development!*