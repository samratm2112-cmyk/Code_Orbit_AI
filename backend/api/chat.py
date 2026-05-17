"""
Chat API Endpoints
FastAPI routes for AI-powered repository chat using Groq
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

from shared.logger import logger
from backend.models.chat import (
    ChatQuery,
    ChatResponse
)
from backend.ai.chat_service import chat_service

# -----------------------------------------------------------------------
# Import from the GLOBAL singleton cache — same object as repository.py
# and chat_service.py all share.
# -----------------------------------------------------------------------
from backend.cache import repository_cache

# Create router
router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/query", response_model=ChatResponse)
async def query_repository(query: ChatQuery) -> ChatResponse:
    """
    Ask a question about a repository using Groq
    
    This endpoint:
    1. Retrieves repository analysis from cache
    2. Builds context from repository data
    3. Uses Groq LLaMA to generate answer
    4. Returns answer with source references
    
    Args:
        query: Chat query with repo_id and question
        
    Returns:
        Chat response with AI-generated answer and sources
    """
    try:
        logger.info(f"=== Chat Query Request ===")
        logger.info(f"Repo ID: {query.repo_id}")
        logger.info(f"Question: {query.question}")
        logger.info(f"Max Results: {query.max_results}")
        logger.info(f"Include Sources: {query.include_sources}")
        
        # Check if chat service is available
        if not chat_service.is_available():
            logger.error("Groq API not configured")
            raise HTTPException(
                status_code=503,
                detail="Groq API not configured. Please set GROQ_API_KEY in your .env file"
            )
        
        # Process query with Groq
        logger.info("Calling chat_service.query()...")
        response = await chat_service.query(query)
        logger.success(f"Chat query completed successfully")
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions/{repo_id}")
async def get_suggested_questions(repo_id: str):
    """
    Get suggested questions for a repository
    
    Args:
        repo_id: Repository ID
        
    Returns:
        List of suggested questions
    """
    try:
        suggestions = chat_service.get_suggested_questions(repo_id)
        
        return JSONResponse(content={
            "success": True,
            "repo_id": repo_id,
            "suggestions": suggestions
        })
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/insights/{repo_id}")
async def get_repository_insights(repo_id: str):
    """
    Generate repository insights for dashboard
    """
    try:
        logger.info(f"=== Insights Request ===")
        logger.info(f"Requested repo_id: {repo_id}")
        logger.info(f"Available repos in cache: {list(repository_cache.keys())}")
        
        if repo_id not in repository_cache:
            logger.error(f"Repository {repo_id} not found in cache")
            raise HTTPException(status_code=404, detail=f"Repository {repo_id} not found. Available: {list(repository_cache.keys())[:3]}")

        analysis = repository_cache[repo_id]
        logger.info(f"Successfully retrieved analysis for {repo_id}")
        stats = analysis.statistics
        tech = analysis.technology_stack
        important_files = analysis.important_files or []
        framework_list = tech.frameworks or []

        complexity_label = "Small"
        if stats.total_files >= 150 or stats.total_lines >= 20000:
            complexity_label = "Large"
        elif stats.total_files >= 70 or stats.total_lines >= 8000:
            complexity_label = "Medium"

        overview = (
            f"{analysis.metadata.name} is a {analysis.metadata.branch} branch repository with "
            f"{stats.total_files} files and approximately {stats.total_lines:,} lines of code. "
            f"It uses {', '.join(tech.languages or ['multiple languages'])} "
            f"and includes frameworks such as {', '.join(framework_list) or 'none detected'}.")

        architecture = (
            f"The repository is organized around {len(important_files)} key modules and entry points. "
            f"Important files include {', '.join(important_files[:5]) or 'core project files'}, "
            f"and the folder structure is centered on {', '.join(list(stats.languages_distribution.keys())[:3])} source files.")

        beginner = (
            f"This project contains {stats.total_files} files and is built with "
            f"{', '.join(tech.languages or ['several languages'])}. "
            f"For beginners, start by reading the important files and entry points: "
            f"{', '.join(analysis.entry_points[:3]) or 'project root files'}.")

        return JSONResponse(content={
            "success": True,
            "repo_id": repo_id,
            "data": {
                "project_overview": overview,
                "architecture_summary": architecture,
                "tech_stack": {
                    "languages": tech.languages,
                    "frameworks": tech.frameworks,
                    "tools": tech.tools,
                    "databases": tech.databases
                },
                "beginner_explanation": beginner,
                "key_modules": important_files[:8],
                "complexity_estimate": complexity_label,
                "folder_tree_preview": "\n".join(analysis.folder_structure.split("\n")[:20])
            }
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting repository insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def chat_health_check():
    """Health check for AI chat service"""
    ai_available = chat_service.is_available()
    
    if ai_available:
        status = "healthy"
        note = "Groq API configured - AI chat fully functional"
    else:
        status = "unavailable"
        note = "Groq API key not configured. Set GROQ_API_KEY in .env file"
    
    return JSONResponse(content={
        "status": status,
        "chat_available": ai_available,
        "note": note
    })


# Made with Bob