"""
Pydantic models for repository data structures
Defines schemas for repository analysis, metadata, and responses
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, validator
from enum import Enum


class RepositoryStatus(str, Enum):
    """Repository processing status"""
    PENDING = "pending"
    CLONING = "cloning"
    PARSING = "parsing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileMetadata(BaseModel):
    """Metadata for a single file"""
    path: str = Field(..., description="Relative path from repository root")
    extension: str = Field(..., description="File extension")
    size_bytes: int = Field(..., description="File size in bytes")
    line_count: int = Field(..., description="Number of lines")
    language: Optional[str] = Field(None, description="Programming language")
    content: Optional[str] = Field(None, description="File content")
    
    class Config:
        json_schema_extra = {
            "example": {
                "path": "src/main.py",
                "extension": ".py",
                "size_bytes": 1024,
                "line_count": 45,
                "language": "Python",
                "content": "# Python code here"
            }
        }


class TechnologyStack(BaseModel):
    """Detected technology stack"""
    languages: List[str] = Field(default_factory=list, description="Programming languages")
    frameworks: List[str] = Field(default_factory=list, description="Frameworks detected")
    tools: List[str] = Field(default_factory=list, description="Development tools")
    databases: List[str] = Field(default_factory=list, description="Databases")
    
    class Config:
        json_schema_extra = {
            "example": {
                "languages": ["Python", "JavaScript"],
                "frameworks": ["FastAPI", "React"],
                "tools": ["Docker", "Git"],
                "databases": ["PostgreSQL"]
            }
        }


class RepositoryStatistics(BaseModel):
    """Repository statistics"""
    total_files: int = Field(..., description="Total number of files")
    total_source_files: int = Field(..., description="Number of source code files")
    total_lines: int = Field(..., description="Total lines of code")
    total_size_bytes: int = Field(..., description="Total repository size in bytes")
    languages_distribution: Dict[str, int] = Field(default_factory=dict, description="File count by language")
    largest_files: List[Dict[str, Any]] = Field(default_factory=list, description="Top 10 largest files")
    file_type_distribution: Dict[str, int] = Field(default_factory=dict, description="File count by extension")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_files": 150,
                "total_source_files": 120,
                "total_lines": 5000,
                "total_size_bytes": 1048576,
                "languages_distribution": {"Python": 80, "JavaScript": 40},
                "largest_files": [{"path": "main.py", "size": 10240}],
                "file_type_distribution": {".py": 80, ".js": 40, ".md": 10}
            }
        }


class FolderNode(BaseModel):
    """Folder tree node"""
    name: str = Field(..., description="Folder or file name")
    type: str = Field(..., description="'file' or 'directory'")
    children: Optional[List['FolderNode']] = Field(None, description="Child nodes")
    size: Optional[int] = Field(None, description="Size in bytes for files")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "src",
                "type": "directory",
                "children": [
                    {"name": "main.py", "type": "file", "size": 1024}
                ]
            }
        }


class RepositoryRequest(BaseModel):
    """Request to analyze a repository"""
    url: str = Field(..., description="GitHub repository URL")
    branch: Optional[str] = Field("main", description="Branch to analyze")
    include_content: bool = Field(True, description="Include file contents in response")
    
    @validator('url')
    def validate_github_url(cls, v):
        """Validate GitHub URL format"""
        if not v:
            raise ValueError("URL cannot be empty")
        
        # Basic GitHub URL validation
        valid_patterns = [
            'github.com/',
            'https://github.com/',
            'http://github.com/',
            'git@github.com:'
        ]
        
        if not any(pattern in v.lower() for pattern in valid_patterns):
            raise ValueError("Must be a valid GitHub repository URL")
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://github.com/fastapi/fastapi",
                "branch": "main",
                "include_content": True
            }
        }


class RepositoryMetadata(BaseModel):
    """Repository metadata"""
    repo_id: str = Field(..., description="Unique repository identifier")
    name: str = Field(..., description="Repository name")
    owner: str = Field(..., description="Repository owner")
    url: str = Field(..., description="Repository URL")
    branch: str = Field(..., description="Analyzed branch")
    clone_path: str = Field(..., description="Local clone path")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    status: RepositoryStatus = Field(default=RepositoryStatus.PENDING, description="Processing status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "repo_id": "fastapi_fastapi_abc123",
                "name": "fastapi",
                "owner": "fastapi",
                "url": "https://github.com/fastapi/fastapi",
                "branch": "main",
                "clone_path": "/data/repositories/fastapi_fastapi_abc123",
                "created_at": "2024-01-01T00:00:00",
                "status": "completed"
            }
        }


class RepositoryAnalysis(BaseModel):
    """Complete repository analysis result"""
    metadata: RepositoryMetadata = Field(..., description="Repository metadata")
    statistics: RepositoryStatistics = Field(..., description="Repository statistics")
    technology_stack: TechnologyStack = Field(..., description="Detected technologies")
    folder_structure: str = Field(..., description="Folder tree as string")
    files: List[FileMetadata] = Field(default_factory=list, description="Parsed files")
    important_files: List[str] = Field(default_factory=list, description="Key files identified")
    entry_points: List[str] = Field(default_factory=list, description="Entry point files")
    
    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {
                    "repo_id": "fastapi_fastapi_abc123",
                    "name": "fastapi",
                    "owner": "fastapi",
                    "url": "https://github.com/fastapi/fastapi",
                    "branch": "main",
                    "clone_path": "/data/repositories/fastapi_fastapi_abc123",
                    "status": "completed"
                },
                "statistics": {
                    "total_files": 150,
                    "total_source_files": 120,
                    "total_lines": 5000,
                    "total_size_bytes": 1048576
                },
                "technology_stack": {
                    "languages": ["Python"],
                    "frameworks": ["FastAPI"],
                    "tools": ["Docker"]
                },
                "folder_structure": "fastapi/\n├── fastapi/\n├── tests/",
                "files": [],
                "important_files": ["README.md", "setup.py"],
                "entry_points": ["main.py"]
            }
        }


class RepositoryResponse(BaseModel):
    """API response for repository analysis"""
    success: bool = Field(..., description="Whether the operation succeeded")
    message: str = Field(..., description="Response message")
    data: Optional[RepositoryAnalysis] = Field(None, description="Analysis data")
    error: Optional[str] = Field(None, description="Error message if failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Repository analyzed successfully",
                "data": {
                    "metadata": {"repo_id": "test_repo"},
                    "statistics": {"total_files": 100}
                },
                "error": None
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = Field(False, description="Always false for errors")
    message: str = Field(..., description="Error message")
    error: str = Field(..., description="Detailed error information")
    error_type: str = Field(..., description="Type of error")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "message": "Failed to clone repository",
                "error": "Repository not found or is private",
                "error_type": "CloneError"
            }
        }


# Update forward references
FolderNode.model_rebuild()

# Made with Bob