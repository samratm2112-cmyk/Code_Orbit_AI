"""
AI Chat Service with Groq API
Handles repository-aware question answering using Groq LLaMA models
"""

import os
import time
from typing import List, Optional, Dict, Any
from datetime import datetime
from groq import Groq

from shared.logger import logger
from shared.config import settings
from backend.models.chat import (
    ChatQuery,
    ChatResponse,
    SourceReference
)

# -----------------------------------------------------------------------
# Use the GLOBAL singleton cache so chat_service always sees the same
# repository data that was stored by the /api/repository/analyze endpoint.
# -----------------------------------------------------------------------
from backend.cache import repository_cache


class ChatService:
    """
    Repository-aware chat service using Groq API
    
    Features:
    - Groq LLaMA 3 70B integration
    - Context-aware responses
    - Source attribution
    - Repository understanding
    """
    
    def __init__(self):
        """Initialize chat service with Groq client"""
        logger.info("ChatService initialized with Groq API")
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Groq client"""
        try:
            if settings.groq_api_key:
                self.client = Groq(api_key=settings.groq_api_key)
                logger.success("Groq client initialized successfully")
            else:
                logger.warning("Groq API key not configured")
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {str(e)}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if chat service is available"""
        return self.client is not None and settings.groq_api_key is not None
    
    async def query(self, chat_query: ChatQuery) -> ChatResponse:
        """
        Answer a question about a repository using Groq
        
        Args:
            chat_query: Chat query request
            
        Returns:
            Chat response with AI-generated answer
        """
        if not self.is_available():
            raise ValueError(
                "Groq API not configured. "
                "Please set GROQ_API_KEY in your .env file"
            )
        
        start_time = time.time()
        logger.info(f"Processing query for repo {chat_query.repo_id}: {chat_query.question}")
        
        try:
            # Debug logging — using global singleton cache
            all_keys = repository_cache.keys()
            logger.info(f"[CACHE LOOKUP] Requested repo_id : '{chat_query.repo_id}'")
            logger.info(f"[CACHE LOOKUP] Available repo_ids: {all_keys}")
            logger.info(f"[CACHE LOOKUP] Cache size        : {len(repository_cache)}")
            
            if chat_query.repo_id not in repository_cache:
                logger.error(f"[CACHE MISS] Repository '{chat_query.repo_id}' NOT in cache")
                logger.error(f"[CACHE MISS] Available repositories: {all_keys}")
                raise ValueError(
                    f"Repository {chat_query.repo_id} not found in cache. "
                    f"Available repositories: {list(all_keys)[:3]}. "
                    "Please analyze the repository first."
                )
            
            analysis = repository_cache[chat_query.repo_id]
            logger.info(f"[CACHE HIT] Successfully retrieved analysis for '{chat_query.repo_id}'")
            
            # Build context from repository analysis
            context = self._build_repository_context(analysis, chat_query.question)
            
            # Generate answer using Groq
            answer = self._generate_answer_with_groq(
                question=chat_query.question,
                context=context,
                repo_name=analysis.metadata.name
            )
            
            # Build source references from relevant files
            sources = []
            if chat_query.include_sources:
                sources = self._build_source_references(analysis, chat_query.question)
            
            processing_time = (time.time() - start_time) * 1000
            logger.success(f"Query processed in {processing_time:.2f}ms")
            
            return ChatResponse(
                success=True,
                answer=answer,
                sources=sources,
                repo_id=chat_query.repo_id,
                question=chat_query.question,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise
    
    def _build_repository_context(self, analysis, question: str) -> str:
        """
        Build context from repository analysis
        
        Args:
            analysis: Repository analysis data
            question: User question
            
        Returns:
            Context string for Groq
        """
        context_parts = []
        
        # Repository metadata
        context_parts.append(f"Repository: {analysis.metadata.name}")
        context_parts.append(f"Owner: {analysis.metadata.owner}")
        context_parts.append(f"Branch: {analysis.metadata.branch}")
        context_parts.append("")
        
        # Statistics
        stats = analysis.statistics
        context_parts.append(f"Total Files: {stats.total_files}")
        context_parts.append(f"Total Lines: {stats.total_lines}")
        context_parts.append(f"Languages: {', '.join(stats.languages_distribution.keys())}")
        context_parts.append("")
        
        # Technology stack
        tech = analysis.technology_stack
        if tech.languages:
            context_parts.append(f"Languages: {', '.join(tech.languages)}")
        if tech.frameworks:
            context_parts.append(f"Frameworks: {', '.join(tech.frameworks)}")
        if tech.tools:
            context_parts.append(f"Tools: {', '.join(tech.tools)}")
        context_parts.append("")
        
        # Important files
        if analysis.important_files:
            context_parts.append("Important Files:")
            for file in analysis.important_files[:10]:
                context_parts.append(f"  - {file}")
            context_parts.append("")
        
        # Entry points
        if analysis.entry_points:
            context_parts.append("Entry Points:")
            for entry in analysis.entry_points[:5]:
                context_parts.append(f"  - {entry}")
            context_parts.append("")
        
        # Folder structure (truncated)
        if analysis.folder_structure:
            lines = analysis.folder_structure.split('\n')[:30]
            context_parts.append("Folder Structure (preview):")
            context_parts.extend(lines)
            context_parts.append("")
        
        # Sample file contents (if available and relevant)
        relevant_files = self._find_relevant_files(analysis, question)
        if relevant_files:
            context_parts.append("Relevant Code Samples:")
            for file in relevant_files[:3]:
                context_parts.append(f"\nFile: {file.path}")
                context_parts.append(f"Language: {file.language}")
                if file.content:
                    # Include first 500 chars of content
                    content_preview = file.content[:500]
                    context_parts.append(f"```{file.language or ''}")
                    context_parts.append(content_preview)
                    if len(file.content) > 500:
                        context_parts.append("... (truncated)")
                    context_parts.append("```")
        
        return "\n".join(context_parts)
    
    def _find_relevant_files(self, analysis, question: str) -> List:
        """
        Find files relevant to the question based on keywords
        
        Args:
            analysis: Repository analysis
            question: User question
            
        Returns:
            List of relevant files
        """
        question_lower = question.lower()
        keywords = question_lower.split()
        
        relevant_files = []
        
        for file in analysis.files:
            if not file.content:
                continue
            
            # Check if file path or content contains keywords
            file_path_lower = file.path.lower()
            content_lower = file.content.lower() if file.content else ""
            
            relevance_score = 0
            for keyword in keywords:
                if len(keyword) > 3:  # Only consider meaningful keywords
                    if keyword in file_path_lower:
                        relevance_score += 2
                    if keyword in content_lower:
                        relevance_score += 1
            
            if relevance_score > 0:
                relevant_files.append((file, relevance_score))
        
        # Sort by relevance and return top files
        relevant_files.sort(key=lambda x: x[1], reverse=True)
        return [file for file, score in relevant_files[:5]]
    
    def _generate_answer_with_groq(
        self,
        question: str,
        context: str,
        repo_name: str
    ) -> str:
        """
        Generate answer using Groq API
        
        Args:
            question: User question
            context: Repository context
            repo_name: Repository name
            
        Returns:
            AI-generated answer
        """
        try:
            system_prompt = f"""You are an expert code analyst helping developers understand the '{repo_name}' repository.

Your role:
- Provide clear, accurate answers about the codebase
- Reference specific files and code when relevant
- Explain technical concepts in an accessible way
- Be concise but thorough
- If you're not certain, say so

Use the provided repository context to answer questions accurately."""

            user_prompt = f"""Repository Context:
{context}

Question: {question}

Please provide a helpful answer based on the repository information above."""

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                model=settings.groq_model,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                top_p=settings.top_p
            )
            
            answer = chat_completion.choices[0].message.content
            logger.info(f"Generated answer with {len(answer)} characters")
            
            return answer
            
        except Exception as e:
            logger.error(f"Groq API error: {str(e)}")
            raise ValueError(f"Failed to generate answer: {str(e)}")
    
    def _build_source_references(
        self,
        analysis,
        question: str
    ) -> List[SourceReference]:
        """
        Build source references from relevant files
        
        Args:
            analysis: Repository analysis
            question: User question
            
        Returns:
            List of source references
        """
        sources = []
        relevant_files = self._find_relevant_files(analysis, question)
        
        for file in relevant_files[:5]:
            # Create preview (first 200 chars)
            preview = file.content.strip()[:200] if file.content else ""
            if len(file.content or "") > 200:
                preview += "..."
            
            source = SourceReference(
                file_path=file.path,
                start_line=1,
                end_line=file.line_count,
                relevance_score=0.8,  # Placeholder score
                content_preview=preview,
                language=file.language
            )
            
            sources.append(source)
        
        return sources
    
    def get_suggested_questions(self, repo_id: str) -> List[str]:
        """
        Get suggested questions for a repository.
        Uses repo context from cache when available for more relevant questions.

        Args:
            repo_id: Repository ID

        Returns:
            List of suggested questions
        """
        # Base questions that work for any repo
        base = [
            "What is the main purpose of this repository?",
            "Where is the entry point of the application?",
            "What is the overall project structure?",
            "How is error handling implemented?",
            "How are environment variables handled?",
        ]

        # Try to enrich with repo-specific questions
        try:
            if repo_id in repository_cache:
                analysis = repository_cache[repo_id]
                tech = analysis.technology_stack
                langs = [l.lower() for l in (tech.languages or [])]
                frameworks = [f.lower() for f in (tech.frameworks or [])]

                extras = []

                # Language-specific suggestions
                if "python" in langs:
                    extras.append("What Python packages or dependencies are used?")
                if "javascript" in langs or "typescript" in langs:
                    extras.append("What npm packages are used?")
                if "go" in langs:
                    extras.append("How are Go modules structured?")
                if "java" in langs:
                    extras.append("How is the Maven/Gradle build configured?")

                # Framework-specific suggestions
                if any(f in frameworks for f in ["fastapi", "django", "flask", "express"]):
                    extras.append("What are the main API endpoints?")
                    extras.append("How is routing configured?")
                if any(f in frameworks for f in ["react", "vue", "angular", "next.js", "nextjs"]):
                    extras.append("How is the frontend state managed?")
                    extras.append("What components are in this project?")
                if any(f in frameworks for f in ["pytest", "jest", "junit", "mocha"]):
                    extras.append("What testing framework is used and how are tests run?")
                if any(f in frameworks for f in ["postgresql", "mysql", "sqlite", "mongodb"]):
                    extras.append("How is the database schema defined?")

                return (base + extras)[:10]
        except Exception as e:
            logger.warning(f"Could not generate contextual suggestions for {repo_id}: {e}")

        # Fallback to generic list
        return base + [
            "How is authentication implemented?",
            "What are the main API endpoints?",
            "How is the database configured?",
            "What testing framework is used?",
            "Which files handle routing?",
        ]


# Global instance
chat_service = ChatService()


# Made with Bob