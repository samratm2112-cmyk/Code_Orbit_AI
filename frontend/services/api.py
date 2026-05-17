"""
API Client Service
Handles all communication with the FastAPI backend
"""

import requests
from typing import Optional, Dict, Any
import streamlit as st


class APIClient:
    """
    Client for CodeOrbit AI FastAPI backend
    
    Features:
    - Centralized API communication
    - Error handling
    - Response parsing
    - Loading state management
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize API client
        
        Args:
            base_url: Backend API base URL
        """
        self.base_url = base_url
        self.timeout = 300  # 5 minutes for long operations
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_detail = "Unknown error"
            try:
                error_data = response.json()
                # Check for our custom wrapper first, then fallback to standard FastAPI
                error_detail = error_data.get('message') or error_data.get('error') or error_data.get('detail', str(e))
            except:
                error_detail = str(e)
            raise Exception(f"{error_detail}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
    
    # Repository Endpoints
    
    def analyze_repository(
        self,
        url: str,
        branch: str = "main",
        include_content: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze a GitHub repository
        
        Args:
            url: GitHub repository URL
            branch: Branch to analyze
            include_content: Include file contents
            
        Returns:
            Analysis results
        """
        endpoint = f"{self.base_url}/api/repository/analyze"
        payload = {
            "url": url,
            "branch": branch,
            "include_content": include_content
        }
        
        print(f"[API] Analyzing repository: {url}")
        print(f"[API] Endpoint: {endpoint}")
        
        try:
            response = requests.post(endpoint, json=payload, timeout=self.timeout)
            result = self._handle_response(response)
            print(f"[API] Analysis successful")
            return result
        except Exception as e:
            print(f"[API] Analysis failed: {str(e)}")
            raise
    
    def get_repository_summary(self, repo_id: str) -> Dict[str, Any]:
        """Get repository summary"""
        endpoint = f"{self.base_url}/api/repository/{repo_id}/summary"
        response = requests.get(endpoint, timeout=30)
        return self._handle_response(response)
    
    def get_repository_structure(self, repo_id: str) -> Dict[str, Any]:
        """Get repository structure"""
        endpoint = f"{self.base_url}/api/repository/{repo_id}/structure"
        response = requests.get(endpoint, timeout=30)
        return self._handle_response(response)
    
    def get_repository_statistics(self, repo_id: str) -> Dict[str, Any]:
        """Get repository statistics"""
        endpoint = f"{self.base_url}/api/repository/{repo_id}/statistics"
        response = requests.get(endpoint, timeout=30)
        return self._handle_response(response)
    
    def list_repositories(self) -> Dict[str, Any]:
        """List all analyzed repositories"""
        endpoint = f"{self.base_url}/api/repository/list"
        response = requests.get(endpoint, timeout=30)
        return self._handle_response(response)
    
    def delete_repository(self, repo_id: str) -> Dict[str, Any]:
        """Delete a repository"""
        endpoint = f"{self.base_url}/api/repository/{repo_id}"
        response = requests.delete(endpoint, timeout=30)
        return self._handle_response(response)
    
    # Chat Endpoints (OpenAI-based)
    
    def query_repository(
        self,
        repo_id: str,
        question: str,
        max_results: int = 5,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Ask a question about a repository
        
        Args:
            repo_id: Repository ID
            question: User question
            max_results: Maximum results to return
            include_sources: Include source references
            
        Returns:
            Chat response with answer and sources
        """
        endpoint = f"{self.base_url}/api/chat/query"
        payload = {
            "repo_id": repo_id,
            "question": question,
            "max_results": max_results,
            "include_sources": include_sources
        }
        
        response = requests.post(endpoint, json=payload, timeout=60)
        return self._handle_response(response)
    
    def get_repository_insights(self, repo_id: str) -> Dict[str, Any]:
        """Get repository insights for the AI dashboard"""
        endpoint = f"{self.base_url}/api/chat/insights/{repo_id}"
        response = requests.get(endpoint, timeout=30)
        return self._handle_response(response)
    
    def get_suggested_questions(self, repo_id: str) -> Dict[str, Any]:
        """Get suggested questions"""
        endpoint = f"{self.base_url}/api/chat/suggestions/{repo_id}"
        response = requests.get(endpoint, timeout=30)
        return self._handle_response(response)
    
    # Health Checks
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        try:
            endpoint = f"{self.base_url}/health"
            response = requests.get(endpoint, timeout=5)
            return self._handle_response(response)
        except Exception as e:
            print(f"[API] Health check failed: {str(e)}")
            raise
    
    def is_backend_available(self) -> bool:
        """Check if backend is available"""
        try:
            response = self.health_check()
            print(f"[API] Backend health check: {response}")
            return response.get('status') == 'healthy'
        except Exception as e:
            print(f"[API] Backend unavailable: {str(e)}")
            return False
    
    def get_ai_status(self) -> Dict[str, Any]:
        """Get AI system status from backend"""
        endpoint = f"{self.base_url}/api/chat/health"
        try:
            response = requests.get(endpoint, timeout=5)
            return self._handle_response(response)
        except Exception as e:
            print(f"[API] AI status unavailable: {str(e)}")
            return {
                "status": "unavailable",
                "chat_available": False,
                "note": "Groq API not configured — repository analysis still works."
            }

    def is_ai_available(self) -> bool:
        """Check if AI chat features are available"""
        status = self.get_ai_status()
        available = status.get("chat_available", False)
        print(f"[API] AI chat available: {available}")
        return available


# Global API client instance
@st.cache_resource
def get_api_client() -> APIClient:
    """Get cached API client instance"""
    return APIClient()


# Made with Bob