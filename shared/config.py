"""
Configuration management for CodeOrbit AI
Loads settings from environment variables with sensible defaults
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "CodeOrbit AI"
    app_version: str = "1.0.0"
    debug: bool = True
    log_level: str = "INFO"
    
    # Groq (Required for AI chat features)
    groq_api_key: Optional[str] = None
    groq_model: str = "llama-3.3-70b-versatile"
    
    # GitHub (Optional)
    github_token: str = ""
    
    # Backend
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_reload: bool = True
    
    # Frontend
    frontend_port: int = 8501
    frontend_host: str = "localhost"
    
    # Storage Paths
    repo_storage_path: Path = BASE_DIR / "data" / "repositories"
    vector_store_path: Path = BASE_DIR / "data" / "vector_stores"
    cache_path: Path = BASE_DIR / "data" / "cache"
    
    # Repository Storage (no vector database needed)
    max_chunks_per_file: int = 50
    
    # Repository Analysis
    max_file_size_mb: int = 5
    max_repo_size_mb: int = 500
    supported_extensions: str = ".py,.js,.jsx,.ts,.tsx,.java,.go,.rs,.cpp,.c,.h,.md,.json,.yaml,.yml"
    ignore_patterns: str = "node_modules,venv,__pycache__,.git,dist,build,*.pyc,*.log"
    
    # LLM Settings
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    
    # Chat Settings
    max_context_chunks: int = 5
    chat_history_limit: int = 20
    streaming_enabled: bool = True
    
    # Rate Limiting
    max_requests_per_minute: int = 60
    max_embeddings_per_batch: int = 100
    
    # Caching
    enable_cache: bool = True
    cache_ttl_seconds: int = 3600
    
    # Security
    cors_origins: str = "http://localhost:8501,http://localhost:3000"
    allowed_hosts: str = "localhost,127.0.0.1"
    
    # Monitoring
    enable_metrics: bool = False
    sentry_dsn: str = ""
    
    # Development
    dev_mode: bool = True
    mock_responses: bool = False
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def supported_extensions_list(self) -> List[str]:
        """Get supported extensions as a list"""
        return [ext.strip() for ext in self.supported_extensions.split(",")]
    
    @property
    def ignore_patterns_list(self) -> List[str]:
        """Get ignore patterns as a list"""
        return [pattern.strip() for pattern in self.ignore_patterns.split(",")]
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def allowed_hosts_list(self) -> List[str]:
        """Get allowed hosts as a list"""
        return [host.strip() for host in self.allowed_hosts.split(",")]
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        self.repo_storage_path.mkdir(parents=True, exist_ok=True)
        self.vector_store_path.mkdir(parents=True, exist_ok=True)
        self.cache_path.mkdir(parents=True, exist_ok=True)
    
    def validate_groq_config(self) -> bool:
        """
        Validate Groq configuration
        Returns True if API key is configured, False otherwise
        """
        return self.groq_api_key is not None and len(self.groq_api_key.strip()) > 0
    
    def require_groq(self):
        """
        Raise error if Groq is not configured
        Call this method in LLM-dependent features
        """
        if not self.validate_groq_config():
            raise ValueError(
                "Groq API key is required for AI chat features. "
                "To enable AI chat, set GROQ_API_KEY in your .env file."
            )


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.ensure_directories()

# Log configuration status
import sys
if hasattr(sys.modules.get('shared.logger'), 'logger'):
    from shared.logger import logger
    logger.info(f"Configuration loaded: {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Storage path: {settings.repo_storage_path}")
    
    if settings.validate_groq_config():
        logger.info("✓ Groq API key configured - AI chat features available")
    else:
        logger.warning("⚠️  Groq API key not configured - AI chat features unavailable")

# Made with Bob
