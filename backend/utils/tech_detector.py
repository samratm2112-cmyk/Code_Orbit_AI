"""
Technology Stack Detector
Detects frameworks, libraries, and tools used in a repository
"""

import json
from pathlib import Path
from typing import List, Dict, Set, Optional
import re

from shared.logger import logger
from backend.models.repository import TechnologyStack


class TechnologyDetector:
    """
    Detects technology stack from repository files
    
    Features:
    - Detect programming languages
    - Identify frameworks (React, FastAPI, Flask, etc.)
    - Find tools (Docker, Git, etc.)
    - Parse package managers (npm, pip, cargo, etc.)
    - Analyze imports and dependencies
    """
    
    # Framework detection patterns
    FRAMEWORK_PATTERNS = {
        'React': [
            r'import\s+.*\s+from\s+[\'"]react[\'"]',
            r'require\([\'"]react[\'"]\)',
            r'"react":\s*"',
        ],
        'Next.js': [
            r'import\s+.*\s+from\s+[\'"]next',
            r'"next":\s*"',
            r'next\.config\.',
        ],
        'Vue': [
            r'import\s+.*\s+from\s+[\'"]vue[\'"]',
            r'"vue":\s*"',
        ],
        'Angular': [
            r'@angular/',
            r'"@angular/core"',
        ],
        'FastAPI': [
            r'from\s+fastapi\s+import',
            r'import\s+fastapi',
            r'fastapi==',
        ],
        'Flask': [
            r'from\s+flask\s+import',
            r'import\s+flask',
            r'Flask\(',
        ],
        'Django': [
            r'from\s+django',
            r'import\s+django',
            r'django==',
        ],
        'Express': [
            r'require\([\'"]express[\'"]\)',
            r'import\s+.*\s+from\s+[\'"]express[\'"]',
            r'"express":\s*"',
        ],
        'Streamlit': [
            r'import\s+streamlit',
            r'streamlit==',
        ],
        'LangChain': [
            r'from\s+langchain',
            r'import\s+langchain',
            r'langchain==',
        ],
        'TensorFlow': [
            r'import\s+tensorflow',
            r'tensorflow==',
        ],
        'PyTorch': [
            r'import\s+torch',
            r'torch==',
        ],
        'Tailwind CSS': [
            r'tailwindcss',
            r'@tailwind',
        ],
        'Bootstrap': [
            r'bootstrap',
            r'@import.*bootstrap',
        ],
    }
    
    # Tool detection patterns
    TOOL_PATTERNS = {
        'Docker': ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml', '.dockerignore'],
        'Git': ['.git', '.gitignore', '.gitattributes'],
        'GitHub Actions': ['.github/workflows'],
        'Kubernetes': ['kubernetes/', 'k8s/', '.yaml', 'deployment.yaml'],
        'Terraform': ['.tf', 'terraform'],
        'Makefile': ['Makefile', 'makefile'],
        'Poetry': ['poetry.lock', 'pyproject.toml'],
        'npm': ['package.json', 'package-lock.json'],
        'Yarn': ['yarn.lock'],
        'pip': ['requirements.txt', 'setup.py'],
        'Cargo': ['Cargo.toml', 'Cargo.lock'],
        'Go Modules': ['go.mod', 'go.sum'],
        'Maven': ['pom.xml'],
        'Gradle': ['build.gradle', 'settings.gradle'],
    }
    
    # Database patterns
    DATABASE_PATTERNS = {
        'PostgreSQL': [r'psycopg2', r'postgresql://', r'postgres://'],
        'MySQL': [r'mysql', r'pymysql', r'mysql://'],
        'MongoDB': [r'mongodb://', r'pymongo', r'mongoose'],
        'Redis': [r'redis://', r'redis==', r'import redis'],
        'SQLite': [r'sqlite3', r'sqlite://'],
        'Elasticsearch': [r'elasticsearch', r'elastic'],
        'FAISS': [r'faiss', r'import faiss'],
    }
    
    def __init__(self):
        """Initialize technology detector"""
        logger.info("TechnologyDetector initialized")
    
    def detect_from_files(
        self,
        repo_path: Path,
        file_contents: Optional[Dict[str, str]] = None
    ) -> TechnologyStack:
        """
        Detect technology stack from repository files
        
        Args:
            repo_path: Path to repository
            file_contents: Optional dict of file paths to contents
            
        Returns:
            TechnologyStack object
        """
        languages = self._detect_languages(repo_path)
        frameworks = self._detect_frameworks(repo_path, file_contents)
        tools = self._detect_tools(repo_path)
        databases = self._detect_databases(repo_path, file_contents)
        
        tech_stack = TechnologyStack(
            languages=list(languages),
            frameworks=list(frameworks),
            tools=list(tools),
            databases=list(databases)
        )
        
        logger.info(f"Detected tech stack: {len(languages)} languages, "
                   f"{len(frameworks)} frameworks, {len(tools)} tools, "
                   f"{len(databases)} databases")
        
        return tech_stack
    
    def _detect_languages(self, repo_path: Path) -> Set[str]:
        """Detect programming languages from file extensions"""
        languages = set()
        
        extension_to_language = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.jsx': 'JavaScript',
            '.ts': 'TypeScript',
            '.tsx': 'TypeScript',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.cpp': 'C++',
            '.c': 'C',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.scala': 'Scala',
            '.r': 'R',
            '.sh': 'Shell',
            '.sql': 'SQL',
        }
        
        try:
            for file_path in repo_path.rglob('*'):
                if file_path.is_file():
                    ext = file_path.suffix.lower()
                    if ext in extension_to_language:
                        languages.add(extension_to_language[ext])
        except Exception as e:
            logger.error(f"Error detecting languages: {str(e)}")
        
        return languages
    
    def _detect_frameworks(
        self,
        repo_path: Path,
        file_contents: Optional[Dict[str, str]] = None
    ) -> Set[str]:
        """Detect frameworks from package files and imports"""
        frameworks = set()
        
        # Check package.json
        package_json = repo_path / 'package.json'
        if package_json.exists():
            frameworks.update(self._parse_package_json(package_json))
        
        # Check requirements.txt
        requirements = repo_path / 'requirements.txt'
        if requirements.exists():
            frameworks.update(self._parse_requirements(requirements))
        
        # Check pyproject.toml
        pyproject = repo_path / 'pyproject.toml'
        if pyproject.exists():
            frameworks.update(self._parse_pyproject(pyproject))
        
        # Check Cargo.toml
        cargo = repo_path / 'Cargo.toml'
        if cargo.exists():
            frameworks.update(self._parse_cargo(cargo))
        
        # Check file contents for import patterns
        if file_contents:
            for content in file_contents.values():
                frameworks.update(self._detect_from_content(content, self.FRAMEWORK_PATTERNS))
        
        return frameworks
    
    def _detect_tools(self, repo_path: Path) -> Set[str]:
        """Detect development tools from file presence"""
        tools = set()
        
        for tool, patterns in self.TOOL_PATTERNS.items():
            for pattern in patterns:
                # Check if file or directory exists
                if (repo_path / pattern).exists():
                    tools.add(tool)
                    break
                
                # Check with glob pattern
                try:
                    if list(repo_path.glob(f"**/{pattern}")):
                        tools.add(tool)
                        break
                except Exception:
                    continue
        
        return tools
    
    def _detect_databases(
        self,
        repo_path: Path,
        file_contents: Optional[Dict[str, str]] = None
    ) -> Set[str]:
        """Detect databases from dependencies and code"""
        databases = set()
        
        # Check requirements.txt
        requirements = repo_path / 'requirements.txt'
        if requirements.exists():
            try:
                content = requirements.read_text()
                for db, patterns in self.DATABASE_PATTERNS.items():
                    if any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns):
                        databases.add(db)
            except Exception as e:
                logger.error(f"Error reading requirements.txt: {str(e)}")
        
        # Check package.json
        package_json = repo_path / 'package.json'
        if package_json.exists():
            try:
                content = package_json.read_text()
                for db, patterns in self.DATABASE_PATTERNS.items():
                    if any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns):
                        databases.add(db)
            except Exception as e:
                logger.error(f"Error reading package.json: {str(e)}")
        
        # Check file contents
        if file_contents:
            for content in file_contents.values():
                databases.update(self._detect_from_content(content, self.DATABASE_PATTERNS))
        
        return databases
    
    def _parse_package_json(self, file_path: Path) -> Set[str]:
        """Parse package.json for frameworks"""
        frameworks = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                dependencies = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                
                framework_map = {
                    'react': 'React',
                    'next': 'Next.js',
                    'vue': 'Vue',
                    '@angular/core': 'Angular',
                    'express': 'Express',
                    'tailwindcss': 'Tailwind CSS',
                    'bootstrap': 'Bootstrap',
                }
                
                for dep in dependencies:
                    for key, framework in framework_map.items():
                        if key in dep.lower():
                            frameworks.add(framework)
        
        except Exception as e:
            logger.error(f"Error parsing package.json: {str(e)}")
        
        return frameworks
    
    def _parse_requirements(self, file_path: Path) -> Set[str]:
        """Parse requirements.txt for frameworks"""
        frameworks = set()
        
        try:
            content = file_path.read_text()
            
            framework_map = {
                'fastapi': 'FastAPI',
                'flask': 'Flask',
                'django': 'Django',
                'streamlit': 'Streamlit',
                'langchain': 'LangChain',
                'tensorflow': 'TensorFlow',
                'torch': 'PyTorch',
            }
            
            for line in content.lower().split('\n'):
                for key, framework in framework_map.items():
                    if key in line:
                        frameworks.add(framework)
        
        except Exception as e:
            logger.error(f"Error parsing requirements.txt: {str(e)}")
        
        return frameworks
    
    def _parse_pyproject(self, file_path: Path) -> Set[str]:
        """Parse pyproject.toml for frameworks"""
        frameworks = set()
        
        try:
            content = file_path.read_text()
            
            framework_map = {
                'fastapi': 'FastAPI',
                'flask': 'Flask',
                'django': 'Django',
                'streamlit': 'Streamlit',
            }
            
            for key, framework in framework_map.items():
                if key in content.lower():
                    frameworks.add(framework)
        
        except Exception as e:
            logger.error(f"Error parsing pyproject.toml: {str(e)}")
        
        return frameworks
    
    def _parse_cargo(self, file_path: Path) -> Set[str]:
        """Parse Cargo.toml for Rust frameworks"""
        frameworks = set()
        
        try:
            content = file_path.read_text()
            
            if 'actix-web' in content:
                frameworks.add('Actix Web')
            if 'rocket' in content:
                frameworks.add('Rocket')
            if 'tokio' in content:
                frameworks.add('Tokio')
        
        except Exception as e:
            logger.error(f"Error parsing Cargo.toml: {str(e)}")
        
        return frameworks
    
    def _detect_from_content(
        self,
        content: str,
        patterns: Dict[str, List[str]]
    ) -> Set[str]:
        """Detect technologies from file content using regex patterns"""
        detected = set()
        
        for tech, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, content, re.IGNORECASE):
                    detected.add(tech)
                    break
        
        return detected


# Made with Bob