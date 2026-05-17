"""
Repository API Endpoints
FastAPI routes for repository analysis operations
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional
import asyncio

from shared.logger import logger
from backend.models.repository import (
    RepositoryRequest,
    RepositoryResponse,
    RepositoryAnalysis,
    ErrorResponse
)
from backend.core.repo_parser import RepositoryParser

# -----------------------------------------------------------------------
# Import the GLOBAL singleton cache so that ALL modules in the backend
# (repository.py, chat.py, chat_service.py, etc.) share the exact same
# dict object — even across uvicorn --reload cycles.
# -----------------------------------------------------------------------
from backend.cache import repository_cache

# Create router
router = APIRouter(prefix="/api/repository", tags=["repository"])

# Initialize parser
repo_parser = RepositoryParser()


@router.post("/analyze", response_model=RepositoryResponse)
async def analyze_repository(
    request: RepositoryRequest,
    background_tasks: BackgroundTasks
) -> RepositoryResponse:
    """
    Analyze a GitHub repository
    
    This endpoint:
    1. Clones the repository
    2. Parses all files
    3. Detects technology stack
    4. Generates statistics
    5. Creates folder tree
    6. Returns complete analysis
    
    Args:
        request: Repository analysis request
        background_tasks: FastAPI background tasks
        
    Returns:
        RepositoryResponse with analysis data
    """
    try:
        logger.info(f"Received analysis request for: {request.url}")
        
        # Validate URL
        if not request.url:
            raise HTTPException(status_code=400, detail="Repository URL is required")
        
        # Ensure branch is not None
        branch: str = request.branch if request.branch is not None else "main"
        
        # Parse repository
        analysis = await repo_parser.parse_repository(
            url=request.url,
            branch=branch,
            include_content=request.include_content
        )
        
        # Cache the analysis using the global singleton cache
        repo_id = analysis.metadata.repo_id
        repository_cache[repo_id] = analysis
        
        # Verbose registration logging
        logger.success(f"[CACHE] Repository REGISTERED: {repo_id}")
        logger.info(f"[CACHE] Total cached repos: {len(repository_cache)}")
        logger.info(f"[CACHE] All repo IDs in cache: {repository_cache.keys()}")
        logger.info(f"[CACHE] Cache object id: {id(repository_cache)}")
        
        logger.success(f"Analysis completed: {repo_id}")
        
        return RepositoryResponse(
            success=True,
            message="Repository analyzed successfully",
            data=analysis,
            error=None
        )
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze repository: {str(e)}"
        )


@router.get("/{repo_id}/summary")
async def get_repository_summary(repo_id: str):
    """
    Get summary of a previously analyzed repository
    
    Args:
        repo_id: Repository ID
        
    Returns:
        Repository summary
    """
    try:
        if repo_id not in repository_cache:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        analysis = repository_cache[repo_id]
        summary = repo_parser.get_repository_summary(analysis)
        
        return JSONResponse(content={
            "success": True,
            "data": summary
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repo_id}/structure")
async def get_repository_structure(repo_id: str):
    """
    Get folder structure of a repository
    
    Args:
        repo_id: Repository ID
        
    Returns:
        Folder structure
    """
    try:
        if repo_id not in repository_cache:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        analysis = repository_cache[repo_id]
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "folder_structure": analysis.folder_structure,
                "important_files": analysis.important_files,
                "entry_points": analysis.entry_points
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get structure: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repo_id}/statistics")
async def get_repository_statistics(repo_id: str):
    """
    Get detailed statistics of a repository
    
    Args:
        repo_id: Repository ID
        
    Returns:
        Repository statistics
    """
    try:
        if repo_id not in repository_cache:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        analysis = repository_cache[repo_id]
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "statistics": analysis.statistics.model_dump(),
                "technology_stack": analysis.technology_stack.model_dump()
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repo_id}/files")
async def get_repository_files(
    repo_id: str,
    limit: Optional[int] = 100,
    language: Optional[str] = None
):
    """
    Get files from a repository with optional filtering
    
    Args:
        repo_id: Repository ID
        limit: Maximum number of files to return
        language: Filter by programming language
        
    Returns:
        List of files
    """
    try:
        if repo_id not in repository_cache:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        analysis = repository_cache[repo_id]
        files = analysis.files
        
        # Filter by language if specified
        if language:
            files = [f for f in files if f.language == language]
        
        # Limit results
        files = files[:limit]
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "total": len(analysis.files),
                "returned": len(files),
                "files": [f.model_dump(exclude={'content'}) for f in files]
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{repo_id}/file/{file_path:path}")
async def get_file_content(repo_id: str, file_path: str):
    """
    Get content of a specific file
    
    Args:
        repo_id: Repository ID
        file_path: Path to file
        
    Returns:
        File content and metadata
    """
    try:
        if repo_id not in repository_cache:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        analysis = repository_cache[repo_id]
        
        # Find file
        file_metadata = None
        for f in analysis.files:
            if f.path == file_path:
                file_metadata = f
                break
        
        if not file_metadata:
            raise HTTPException(status_code=404, detail="File not found")
        
        return JSONResponse(content={
            "success": True,
            "data": file_metadata.model_dump()
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{repo_id}")
async def delete_repository(repo_id: str):
    """
    Delete a repository from cache and disk
    
    Args:
        repo_id: Repository ID
        
    Returns:
        Success message
    """
    try:
        if repo_id not in repository_cache:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        # Remove from cache
        del repository_cache[repo_id]
        
        # Cleanup from disk
        repo_parser.cleanup_repository(repo_id)
        
        logger.info(f"Repository deleted: {repo_id}")
        
        return JSONResponse(content={
            "success": True,
            "message": "Repository deleted successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete repository: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_repositories():
    """
    List all analyzed repositories
    
    Returns:
        List of repository summaries
    """
    try:
        summaries = []
        
        for repo_id, analysis in repository_cache.items():
            summary = {
                "repo_id": repo_id,
                "name": analysis.metadata.name,
                "owner": analysis.metadata.owner,
                "url": analysis.metadata.url,
                "status": analysis.metadata.status,
                "analyzed_at": analysis.metadata.created_at.isoformat(),
                "total_files": analysis.statistics.total_files,
                "languages": list(analysis.statistics.languages_distribution.keys())[:3]
            }
            summaries.append(summary)
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "total": len(summaries),
                "repositories": summaries
            }
        })
        
    except Exception as e:
        logger.error(f"Failed to list repositories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{repo_id}/prepare-embeddings")
async def prepare_embeddings(repo_id: str, max_files: int = 100):
    """
    Prepare repository data for embedding generation
    
    Args:
        repo_id: Repository ID
        max_files: Maximum number of files to include
        
    Returns:
        Documents ready for embedding
    """
    try:
        if repo_id not in repository_cache:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        analysis = repository_cache[repo_id]
        documents = repo_parser.prepare_for_embeddings(analysis, max_files)
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "total_documents": len(documents),
                "documents": documents
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to prepare embeddings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(content={
        "status": "healthy",
        "service": "repository-analysis",
        "cached_repositories": len(repository_cache)
    })


# Made with Bob