"""
Constants used across CodeOrbit AI
"""

# File size limits (in bytes)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_REPO_SIZE = 500 * 1024 * 1024  # 500 MB

# Supported programming languages and their extensions
LANGUAGE_EXTENSIONS = {
    "Python": [".py", ".pyw"],
    "JavaScript": [".js", ".jsx", ".mjs"],
    "TypeScript": [".ts", ".tsx"],
    "Java": [".java"],
    "Go": [".go"],
    "Rust": [".rs"],
    "C++": [".cpp", ".cc", ".cxx", ".hpp", ".h"],
    "C": [".c", ".h"],
    "Ruby": [".rb"],
    "PHP": [".php"],
    "Swift": [".swift"],
    "Kotlin": [".kt", ".kts"],
    "Scala": [".scala"],
    "R": [".r", ".R"],
    "Shell": [".sh", ".bash"],
    "SQL": [".sql"],
    "HTML": [".html", ".htm"],
    "CSS": [".css", ".scss", ".sass", ".less"],
    "Markdown": [".md", ".markdown"],
    "JSON": [".json"],
    "YAML": [".yaml", ".yml"],
    "XML": [".xml"],
    "TOML": [".toml"],
}

# Important file patterns
IMPORTANT_FILES = [
    "README.md",
    "README",
    "CONTRIBUTING.md",
    "LICENSE",
    "setup.py",
    "requirements.txt",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "Makefile",
    "Dockerfile",
    "docker-compose.yml",
    ".gitignore",
    "pyproject.toml",
]

# Directories to ignore
IGNORE_DIRECTORIES = [
    ".git",
    ".github",
    ".vscode",
    ".idea",
    "node_modules",
    "venv",
    "env",
    ".env",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    "target",
    "bin",
    "obj",
    ".next",
    ".nuxt",
    "coverage",
    ".coverage",
    "htmlcov",
]

# File patterns to ignore
IGNORE_PATTERNS = [
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    "*.dll",
    "*.dylib",
    "*.exe",
    "*.log",
    "*.tmp",
    "*.temp",
    "*.swp",
    "*.swo",
    "*.bak",
    "*.DS_Store",
    "*.min.js",
    "*.min.css",
    "*.map",
]

# Code structure patterns
ENTRY_POINT_PATTERNS = [
    "main.py",
    "app.py",
    "index.js",
    "index.ts",
    "main.go",
    "main.rs",
    "Main.java",
    "Program.cs",
]

# Documentation patterns
DOCUMENTATION_PATTERNS = [
    "README*",
    "CHANGELOG*",
    "CONTRIBUTING*",
    "LICENSE*",
    "SECURITY*",
    "CODE_OF_CONDUCT*",
    "docs/**",
    "documentation/**",
]

# Test patterns
TEST_PATTERNS = [
    "test_*.py",
    "*_test.py",
    "tests/**",
    "test/**",
    "*.test.js",
    "*.spec.js",
    "*.test.ts",
    "*.spec.ts",
    "__tests__/**",
]

# Configuration patterns
CONFIG_PATTERNS = [
    "*.json",
    "*.yaml",
    "*.yml",
    "*.toml",
    "*.ini",
    "*.conf",
    "*.config",
    ".env*",
    "Dockerfile",
    "docker-compose*",
]

# Chunk sizes for embeddings
CHUNK_SIZE = 1000  # characters
CHUNK_OVERLAP = 200  # characters

# LLM Prompts
SYSTEM_PROMPTS = {
    "repository_summary": """You are an expert software architect analyzing a code repository. 
Provide a clear, concise summary focusing on:
1. Project purpose and functionality
2. Architecture and design patterns
3. Key technologies and frameworks
4. Main components and their relationships
5. Notable features or innovations""",
    
    "code_qa": """You are an expert code analyst helping developers understand a repository.
Answer questions accurately based on the provided code context.
Include code examples when relevant.
Be concise but thorough.""",
    
    "documentation": """You are a technical writer creating clear, comprehensive documentation.
Write in a professional, accessible style.
Include code examples and practical guidance.
Structure content logically with clear headings.""",
    
    "pr_analysis": """You are a senior code reviewer analyzing pull requests.
Identify potential issues, risks, and improvements.
Focus on code quality, security, and maintainability.
Be constructive and specific in your feedback.""",
}

# Response templates
RESPONSE_TEMPLATES = {
    "analysis_started": "🔍 Analyzing repository: {repo_name}",
    "cloning_repo": "📥 Cloning repository...",
    "parsing_files": "📄 Parsing {file_count} files...",
    "generating_embeddings": "🧠 Generating embeddings...",
    "analysis_complete": "✅ Analysis complete!",
    "error_occurred": "❌ Error: {error_message}",
}

# API response codes
API_RESPONSES = {
    "success": {"status": "success", "code": 200},
    "created": {"status": "created", "code": 201},
    "bad_request": {"status": "error", "code": 400},
    "unauthorized": {"status": "error", "code": 401},
    "not_found": {"status": "error", "code": 404},
    "server_error": {"status": "error", "code": 500},
}

# Feature flags
FEATURES = {
    "pr_analysis": True,
    "code_search": True,
    "documentation_generation": True,
    "architecture_visualization": False,  # Future feature
    "code_suggestions": False,  # Future feature
}

# Made with Bob
