# CodeOrbit AI - API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication
Currently, no authentication is required for the MVP. API keys are managed server-side.

---

## Repository Endpoints

### 1. Analyze Repository
Clones and analyzes a GitHub repository.

**Endpoint:** `POST /api/repository/analyze`

**Request Body:**
```json
{
  "url": "https://github.com/username/repository",
  "branch": "main",
  "deep_analysis": true
}
```

**Parameters:**
- `url` (required): GitHub repository URL
- `branch` (optional): Branch to analyze (default: "main")
- `deep_analysis` (optional): Enable detailed analysis (default: true)

**Response:** `201 Created`
```json
{
  "status": "success",
  "data": {
    "repo_id": "uuid-string",
    "name": "repository",
    "owner": "username",
    "url": "https://github.com/username/repository",
    "branch": "main",
    "status": "analyzing",
    "created_at": "2026-05-15T19:00:00Z"
  }
}
```

**Error Response:** `400 Bad Request`
```json
{
  "status": "error",
  "message": "Invalid GitHub URL",
  "code": 400
}
```

---

### 2. Get Repository Summary
Retrieves the analysis summary for a repository.

**Endpoint:** `GET /api/repository/{repo_id}/summary`

**Path Parameters:**
- `repo_id` (required): Repository UUID

**Response:** `200 OK`
```json
{
  "status": "success",
  "data": {
    "repo_id": "uuid-string",
    "name": "repository",
    "description": "AI-generated repository description",
    "primary_language": "Python",
    "languages": {
      "Python": 75.5,
      "JavaScript": 20.3,
      "HTML": 4.2
    },
    "statistics": {
      "total_files": 150,
      "total_lines": 12500,
      "total_functions": 320,
      "total_classes": 45
    },
    "architecture": {
      "type": "Microservices",
      "patterns": ["MVC", "Repository Pattern"],
      "description": "AI-generated architecture explanation"
    },
    "key_files": [
      {
        "path": "src/main.py",
        "type": "entry_point",
        "importance": "high",
        "description": "Application entry point"
      }
    ],
    "tech_stack": ["FastAPI", "PostgreSQL", "Redis"],
    "summary": "Comprehensive AI-generated summary",
    "analyzed_at": "2026-05-15T19:05:00Z"
  }
}
```

---

### 3. Get Repository Structure
Retrieves the file structure of the repository.

**Endpoint:** `GET /api/repository/{repo_id}/structure`

**Query Parameters:**
- `max_depth` (optional): Maximum directory depth (default: 5)
- `include_ignored` (optional): Include ignored files (default: false)

**Response:** `200 OK`
```json
{
  "status": "success",
  "data": {
    "repo_id": "uuid-string",
    "structure": {
      "name": "repository",
      "type": "directory",
      "children": [
        {
          "name": "src",
          "type": "directory",
          "children": [
            {
              "name": "main.py",
              "type": "file",
              "size": 2048,
              "language": "Python"
            }
          ]
        }
      ]
    }
  }
}
```

---

### 4. Get Repository Files
Lists all files in the repository with metadata.

**Endpoint:** `GET /api/repository/{repo_id}/files`

**Query Parameters:**
- `language` (optional): Filter by language
- `type` (optional): Filter by type (source, test, config, docs)
- `limit` (optional): Number of results (default: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response:** `200 OK`
```json
{
  "status": "success",
  "data": {
    "total": 150,
    "files": [
      {
        "path": "src/main.py",
        "language": "Python",
        "type": "source",
        "size": 2048,
        "lines": 85,
        "functions": 5,
        "classes": 2,
        "complexity": "medium"
      }
    ]
  }
}
```

---

### 5. Delete Repository
Removes a repository and its analysis data.

**Endpoint:** `DELETE /api/repository/{repo_id}`

**Response:** `200 OK`
```json
{
  "status": "success",
  "message": "Repository deleted successfully"
}
```

---

## Chat Endpoints

### 1. Query Repository
Ask questions about the repository.

**Endpoint:** `POST /api/chat/query`

**Request Body:**
```json
{
  "repo_id": "uuid-string",
  "question": "How does authentication work in this project?",
  "stream": true,
  "include_context": true
}
```

**Parameters:**
- `repo_id` (required): Repository UUID
- `question` (required): User question
- `stream` (optional): Enable streaming response (default: true)
- `include_context` (optional): Include code context (default: true)

**Response (Non-streaming):** `200 OK`
```json
{
  "status": "success",
  "data": {
    "answer": "Authentication in this project uses JWT tokens...",
    "context": [
      {
        "file": "src/auth.py",
        "content": "def authenticate_user(...):",
        "relevance": 0.95
      }
    ],
    "sources": ["src/auth.py", "src/middleware.py"]
  }
}
```

**Response (Streaming):** `200 OK`
```
Content-Type: text/event-stream

data: {"type": "start", "message": "Searching repository..."}

data: {"type": "context", "files": ["src/auth.py"]}

data: {"type": "chunk", "content": "Authentication in this project"}

data: {"type": "chunk", "content": " uses JWT tokens..."}

data: {"type": "end", "sources": ["src/auth.py"]}
```

---

### 2. Get Chat History
Retrieves conversation history for a repository.

**Endpoint:** `GET /api/chat/{repo_id}/history`

**Query Parameters:**
- `limit` (optional): Number of messages (default: 20)

**Response:** `200 OK`
```json
{
  "status": "success",
  "data": {
    "messages": [
      {
        "role": "user",
        "content": "How does authentication work?",
        "timestamp": "2026-05-15T19:10:00Z"
      },
      {
        "role": "assistant",
        "content": "Authentication uses JWT tokens...",
        "timestamp": "2026-05-15T19:10:05Z"
      }
    ]
  }
}
```

---

### 3. Clear Chat History
Clears conversation history for a repository.

**Endpoint:** `POST /api/chat/{repo_id}/clear`

**Response:** `200 OK`
```json
{
  "status": "success",
  "message": "Chat history cleared"
}
```

---

## Documentation Endpoints

### 1. Generate README
Generates a README.md file for the repository.

**Endpoint:** `POST /api/docs/generate-readme`

**Request Body:**
```json
{
  "repo_id": "uuid-string",
  "style": "comprehensive",
  "include_badges": true,
  "include_examples": true
}
```

**Parameters:**
- `repo_id` (required): Repository UUID
- `style` (optional): "minimal", "standard", "comprehensive" (default: "standard")
- `include_badges` (optional): Add badges (default: true)
- `include_examples` (optional): Add usage examples (default: true)

**Response:** `200 OK`
```json
{
  "status": "success",
  "data": {
    "content": "# Project Name\n\n## Description\n...",
    "format": "markdown",
    "sections": [
      "title",
      "description",
      "installation",
      "usage",
      "contributing"
    ]
  }
}
```

---

### 2. Generate Onboarding Guide
Creates an onboarding guide for new developers.

**Endpoint:** `POST /api/docs/generate-onboarding`

**Request Body:**
```json
{
  "repo_id": "uuid-string",
  "target_audience": "junior",
  "include_setup": true
}
```

**Parameters:**
- `repo_id` (required): Repository UUID
- `target_audience` (optional): "junior", "mid", "senior" (default: "mid")
- `include_setup` (optional): Include setup instructions (default: true)

**Response:** `200 OK`
```json
{
  "status": "success",
  "data": {
    "content": "# Onboarding Guide\n\n## Getting Started\n...",
    "format": "markdown",
    "estimated_time": "2 hours"
  }
}
```

---

### 3. Download Documentation
Downloads generated documentation.

**Endpoint:** `GET /api/docs/{repo_id}/download`

**Query Parameters:**
- `type` (required): "readme", "onboarding", "api"
- `format` (optional): "markdown", "pdf", "html" (default: "markdown")

**Response:** `200 OK`
```
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="README.md"

[File content]
```

---

## PR Analysis Endpoints

### 1. Analyze Pull Request
Analyzes a pull request for risks and improvements.

**Endpoint:** `POST /api/pr/analyze`

**Request Body:**
```json
{
  "repo_id": "uuid-string",
  "pr_url": "https://github.com/username/repository/pull/123",
  "check_security": true,
  "check_performance": true
}
```

**Parameters:**
- `repo_id` (required): Repository UUID
- `pr_url` (required): Pull request URL
- `check_security` (optional): Security analysis (default: true)
- `check_performance` (optional): Performance analysis (default: true)

**Response:** `200 OK`
```json
{
  "status": "success",
  "data": {
    "pr_id": "uuid-string",
    "pr_number": 123,
    "title": "Add authentication feature",
    "status": "analyzed",
    "risk_level": "medium",
    "summary": "This PR adds JWT authentication...",
    "analyzed_at": "2026-05-15T19:15:00Z"
  }
}
```

---

### 2. Get PR Risks
Retrieves identified risks in a pull request.

**Endpoint:** `GET /api/pr/{pr_id}/risks`

**Response:** `200 OK`
```json
{
  "status": "success",
  "data": {
    "risks": [
      {
        "type": "security",
        "severity": "high",
        "file": "src/auth.py",
        "line": 45,
        "description": "Hardcoded secret key detected",
        "recommendation": "Use environment variables"
      },
      {
        "type": "performance",
        "severity": "medium",
        "file": "src/database.py",
        "line": 120,
        "description": "N+1 query detected",
        "recommendation": "Use eager loading"
      }
    ]
  }
}
```

---

### 3. Get PR Summary
Retrieves a summary of the pull request.

**Endpoint:** `GET /api/pr/{pr_id}/summary`

**Response:** `200 OK`
```json
{
  "status": "success",
  "data": {
    "summary": "This PR adds JWT authentication with refresh tokens...",
    "changes": {
      "files_changed": 8,
      "lines_added": 250,
      "lines_removed": 45
    },
    "impact": {
      "scope": "medium",
      "breaking_changes": false,
      "test_coverage": 85.5
    },
    "recommendations": [
      "Add integration tests for auth flow",
      "Update API documentation"
    ]
  }
}
```

---

## Health & Status Endpoints

### 1. Health Check
Checks API health status.

**Endpoint:** `GET /api/health`

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-05-15T19:20:00Z"
}
```

---

### 2. Service Status
Checks status of all services.

**Endpoint:** `GET /api/status`

**Response:** `200 OK`
```json
{
  "status": "operational",
  "services": {
    "api": "healthy",
    "database": "healthy",
    "vector_store": "healthy",
    "llm": "healthy"
  },
  "metrics": {
    "repositories_analyzed": 42,
    "queries_processed": 1250,
    "uptime_seconds": 86400
  }
}
```

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "status": "error",
  "message": "Invalid request parameters",
  "code": 400,
  "details": {
    "field": "url",
    "error": "Invalid GitHub URL format"
  }
}
```

### 404 Not Found
```json
{
  "status": "error",
  "message": "Repository not found",
  "code": 404
}
```

### 429 Too Many Requests
```json
{
  "status": "error",
  "message": "Rate limit exceeded",
  "code": 429,
  "retry_after": 60
}
```

### 500 Internal Server Error
```json
{
  "status": "error",
  "message": "Internal server error",
  "code": 500,
  "request_id": "uuid-string"
}
```

---

## Rate Limiting

- **Default Limit:** 60 requests per minute per IP
- **Burst Limit:** 10 requests per second
- **Headers:**
  - `X-RateLimit-Limit`: Maximum requests per minute
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Time when limit resets (Unix timestamp)

---

## Webhooks (Future Feature)

### Repository Analysis Complete
```json
{
  "event": "repository.analyzed",
  "repo_id": "uuid-string",
  "status": "completed",
  "timestamp": "2026-05-15T19:25:00Z"
}
```

---

## SDK Examples

### Python
```python
import requests

# Analyze repository
response = requests.post(
    "http://localhost:8000/api/repository/analyze",
    json={"url": "https://github.com/username/repo"}
)
repo_data = response.json()

# Query repository
response = requests.post(
    "http://localhost:8000/api/chat/query",
    json={
        "repo_id": repo_data["data"]["repo_id"],
        "question": "How does authentication work?"
    }
)
answer = response.json()
```

### JavaScript
```javascript
// Analyze repository
const response = await fetch('http://localhost:8000/api/repository/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ url: 'https://github.com/username/repo' })
});
const repoData = await response.json();

// Query repository
const chatResponse = await fetch('http://localhost:8000/api/chat/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    repo_id: repoData.data.repo_id,
    question: 'How does authentication work?'
  })
});
const answer = await chatResponse.json();
```

---

## Changelog

### v1.0.0 (2026-05-15)
- Initial API release
- Repository analysis endpoints
- Chat functionality
- Documentation generation
- PR analysis (basic)

---

## Support

For API issues or questions:
- GitHub Issues: https://github.com/username/codeorbit-ai/issues
- Email: support@codeorbit.ai