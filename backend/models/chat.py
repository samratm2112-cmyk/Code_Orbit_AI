"""
Chat and AI-related Pydantic models
Defines schemas for embeddings, chat queries, and responses
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class EmbeddingStatus(str, Enum):
    """Status of embedding generation"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ChunkMetadata(BaseModel):
    """Metadata for a code chunk"""
    chunk_id: str = Field(..., description="Unique chunk identifier")
    repo_id: str = Field(..., description="Repository ID")
    file_path: str = Field(..., description="Source file path")
    language: Optional[str] = Field(None, description="Programming language")
    start_line: int = Field(..., description="Starting line number")
    end_line: int = Field(..., description="Ending line number")
    chunk_index: int = Field(..., description="Chunk index in file")
    total_chunks: int = Field(..., description="Total chunks in file")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chunk_id": "repo123_file1_chunk0",
                "repo_id": "repo123",
                "file_path": "src/main.py",
                "language": "Python",
                "start_line": 1,
                "end_line": 50,
                "chunk_index": 0,
                "total_chunks": 3
            }
        }


class CodeChunk(BaseModel):
    """A chunk of code with metadata"""
    content: str = Field(..., description="Chunk content")
    metadata: ChunkMetadata = Field(..., description="Chunk metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": "def main():\n    print('Hello')",
                "metadata": {
                    "chunk_id": "repo123_file1_chunk0",
                    "repo_id": "repo123",
                    "file_path": "src/main.py",
                    "language": "Python",
                    "start_line": 1,
                    "end_line": 10,
                    "chunk_index": 0,
                    "total_chunks": 1
                }
            }
        }


class EmbeddingRequest(BaseModel):
    """Request to generate embeddings for a repository"""
    repo_id: str = Field(..., description="Repository ID")
    force_regenerate: bool = Field(False, description="Force regeneration if exists")
    max_chunks: Optional[int] = Field(None, description="Maximum chunks to process")
    
    class Config:
        json_schema_extra = {
            "example": {
                "repo_id": "fastapi_fastapi_abc123",
                "force_regenerate": False,
                "max_chunks": 500
            }
        }


class EmbeddingProgress(BaseModel):
    """Progress of embedding generation"""
    repo_id: str = Field(..., description="Repository ID")
    status: EmbeddingStatus = Field(..., description="Current status")
    total_chunks: int = Field(0, description="Total chunks to process")
    processed_chunks: int = Field(0, description="Chunks processed")
    progress_percentage: float = Field(0.0, description="Progress percentage")
    started_at: Optional[datetime] = Field(None, description="Start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "repo_id": "repo123",
                "status": "in_progress",
                "total_chunks": 100,
                "processed_chunks": 45,
                "progress_percentage": 45.0,
                "started_at": "2024-01-16T12:00:00",
                "completed_at": None,
                "error_message": None
            }
        }


class ChatQuery(BaseModel):
    """Chat query request"""
    repo_id: str = Field(..., description="Repository ID to query")
    question: str = Field(..., description="User question")
    max_results: int = Field(5, description="Maximum relevant chunks to retrieve")
    include_sources: bool = Field(True, description="Include source references")
    
    class Config:
        json_schema_extra = {
            "example": {
                "repo_id": "fastapi_fastapi_abc123",
                "question": "Where is authentication implemented?",
                "max_results": 5,
                "include_sources": True
            }
        }


class SourceReference(BaseModel):
    """Reference to source code"""
    file_path: str = Field(..., description="Source file path")
    start_line: int = Field(..., description="Starting line")
    end_line: int = Field(..., description="Ending line")
    relevance_score: float = Field(..., description="Relevance score (0-1)")
    content_preview: Optional[str] = Field(None, description="Content preview")
    language: Optional[str] = Field(None, description="Programming language")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "src/auth/middleware.py",
                "start_line": 15,
                "end_line": 45,
                "relevance_score": 0.92,
                "content_preview": "def authenticate_user(token: str)...",
                "language": "Python"
            }
        }


class ChatResponse(BaseModel):
    """Chat response with answer and sources"""
    success: bool = Field(..., description="Whether query succeeded")
    answer: str = Field(..., description="AI-generated answer")
    sources: List[SourceReference] = Field(default_factory=list, description="Source references")
    repo_id: str = Field(..., description="Repository ID")
    question: str = Field(..., description="Original question")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "answer": "Authentication is implemented in the middleware...",
                "sources": [
                    {
                        "file_path": "src/auth/middleware.py",
                        "start_line": 15,
                        "end_line": 45,
                        "relevance_score": 0.92,
                        "content_preview": "def authenticate_user...",
                        "language": "Python"
                    }
                ],
                "repo_id": "repo123",
                "question": "Where is authentication implemented?",
                "processing_time_ms": 1250.5
            }
        }


class VectorStoreInfo(BaseModel):
    """Information about vector store"""
    repo_id: str = Field(..., description="Repository ID")
    exists: bool = Field(..., description="Whether vector store exists")
    total_vectors: int = Field(0, description="Total vectors stored")
    dimension: int = Field(1536, description="Vector dimension")
    created_at: Optional[datetime] = Field(None, description="Creation time")
    last_updated: Optional[datetime] = Field(None, description="Last update time")
    index_path: Optional[str] = Field(None, description="Index file path")
    
    class Config:
        json_schema_extra = {
            "example": {
                "repo_id": "repo123",
                "exists": True,
                "total_vectors": 250,
                "dimension": 1536,
                "created_at": "2024-01-16T12:00:00",
                "last_updated": "2024-01-16T12:05:00",
                "index_path": "./data/vector_stores/repo123.faiss"
            }
        }


class ChatHistoryItem(BaseModel):
    """Single chat history item"""
    question: str = Field(..., description="User question")
    answer: str = Field(..., description="AI answer")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp")
    sources_count: int = Field(0, description="Number of sources used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Where is authentication implemented?",
                "answer": "Authentication is implemented in...",
                "timestamp": "2024-01-16T12:00:00",
                "sources_count": 3
            }
        }


class ChatSession(BaseModel):
    """Chat session for a repository"""
    repo_id: str = Field(..., description="Repository ID")
    session_id: str = Field(..., description="Session ID")
    history: List[ChatHistoryItem] = Field(default_factory=list, description="Chat history")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session start")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Last activity")
    
    class Config:
        json_schema_extra = {
            "example": {
                "repo_id": "repo123",
                "session_id": "session_abc",
                "history": [],
                "created_at": "2024-01-16T12:00:00",
                "last_activity": "2024-01-16T12:05:00"
            }
        }


# Made with Bob