"""
GitHub Repository Cloning Service
Handles cloning of GitHub repositories with error handling and validation
"""

import os
import re
import shutil
import hashlib
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime
from git import Repo, GitCommandError
from urllib.parse import urlparse

from shared.logger import logger
from shared.config import settings
from backend.models.repository import RepositoryMetadata, RepositoryStatus


class RepositoryCloner:
    """
    Service for cloning GitHub repositories
    
    Features:
    - Clone public GitHub repositories
    - Validate GitHub URLs
    - Handle invalid URLs and errors
    - Avoid duplicate cloning
    - Create unique temp folders
    - Proper exception handling
    - Comprehensive logging
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize the repository cloner
        
        Args:
            storage_path: Path where repositories will be cloned
        """
        self.storage_path = storage_path or settings.repo_storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"RepositoryCloner initialized with storage path: {self.storage_path}")
    
    def validate_github_url(self, url: str) -> bool:
        """
        Validate if the URL is a valid GitHub repository URL
        
        Args:
            url: GitHub repository URL
            
        Returns:
            True if valid, False otherwise
        """
        if not url:
            return False
        
        # Patterns for valid GitHub URLs
        patterns = [
            r'^https?://github\.com/[\w\-]+/[\w\-\.]+/?$',
            r'^https?://github\.com/[\w\-]+/[\w\-\.]+\.git$',
            r'^git@github\.com:[\w\-]+/[\w\-\.]+\.git$',
        ]
        
        # Check if URL matches any pattern
        for pattern in patterns:
            if re.match(pattern, url.strip()):
                return True
        
        # Also accept URLs with additional paths (will be cleaned)
        if 'github.com/' in url:
            return True
        
        return False
    
    def parse_github_url(self, url: str) -> Tuple[str, str]:
        """
        Parse GitHub URL to extract owner and repository name
        
        Args:
            url: GitHub repository URL
            
        Returns:
            Tuple of (owner, repo_name)
            
        Raises:
            ValueError: If URL cannot be parsed
        """
        url = url.strip().rstrip('/')
        
        # Remove .git suffix if present
        if url.endswith('.git'):
            url = url[:-4]
        
        # Handle different URL formats
        if url.startswith('git@github.com:'):
            # SSH format: git@github.com:owner/repo.git
            parts = url.replace('git@github.com:', '').split('/')
        elif 'github.com/' in url:
            # HTTPS format: https://github.com/owner/repo
            parsed = urlparse(url)
            parts = parsed.path.strip('/').split('/')
        else:
            raise ValueError(f"Invalid GitHub URL format: {url}")
        
        if len(parts) < 2:
            raise ValueError(f"Could not extract owner and repo from URL: {url}")
        
        owner = parts[0]
        repo_name = parts[1]
        
        # Clean repo name (remove any query params or fragments)
        repo_name = repo_name.split('?')[0].split('#')[0]
        
        return owner, repo_name
    
    def generate_repo_id(self, owner: str, repo_name: str) -> str:
        """
        Generate a unique repository ID
        
        Args:
            owner: Repository owner
            repo_name: Repository name
            
        Returns:
            Unique repository ID
        """
        # Create a hash of owner and repo name with timestamp
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        unique_string = f"{owner}_{repo_name}_{timestamp}"
        hash_suffix = hashlib.md5(unique_string.encode()).hexdigest()[:8]
        
        return f"{owner}_{repo_name}_{hash_suffix}"
    
    def get_clone_path(self, repo_id: str) -> Path:
        """
        Get the local path where repository will be cloned
        
        Args:
            repo_id: Repository ID
            
        Returns:
            Path object for clone location
        """
        return self.storage_path / repo_id
    
    def clone_repository(
        self,
        url: str,
        branch: str = "main",
        depth: int = 1
    ) -> RepositoryMetadata:
        """
        Clone a GitHub repository
        
        Args:
            url: GitHub repository URL
            branch: Branch to clone (default: main)
            depth: Clone depth (default: 1 for shallow clone)
            
        Returns:
            RepositoryMetadata object with clone information
            
        Raises:
            ValueError: If URL is invalid
            GitCommandError: If cloning fails
            Exception: For other errors
        """
        logger.info(f"Starting repository clone: {url}")
        
        # Validate URL
        if not self.validate_github_url(url):
            error_msg = f"Invalid GitHub URL: {url}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            # Parse URL to get owner and repo name
            owner, repo_name = self.parse_github_url(url)
            logger.info(f"Parsed repository: {owner}/{repo_name}")
            
            # Generate unique repo ID
            repo_id = self.generate_repo_id(owner, repo_name)
            clone_path = self.get_clone_path(repo_id)
            
            # Check if already cloned
            if clone_path.exists():
                logger.warning(f"Repository already exists at {clone_path}, removing...")
                shutil.rmtree(clone_path)
            
            # Normalize URL for cloning
            clone_url = f"https://github.com/{owner}/{repo_name}.git"
            
            # Clone repository
            logger.info(f"Cloning repository to {clone_path}")
            logger.info(f"Branch: {branch}, Depth: {depth}")
            
            try:
                # Try with specified branch
                Repo.clone_from(
                    clone_url,
                    clone_path,
                    branch=branch,
                    depth=depth
                )
                actual_branch = branch
            except GitCommandError as e:
                # If branch doesn't exist, try 'master' as fallback
                if branch == "main":
                    logger.warning(f"Branch 'main' not found, trying 'master'...")
                    try:
                        Repo.clone_from(
                            clone_url,
                            clone_path,
                            branch="master",
                            depth=depth
                        )
                        actual_branch = "master"
                    except GitCommandError:
                        raise e
                else:
                    raise e
            
            logger.success(f"Repository cloned successfully: {repo_id}")
            
            # Create metadata
            metadata = RepositoryMetadata(
                repo_id=repo_id,
                name=repo_name,
                owner=owner,
                url=url,
                branch=actual_branch,
                clone_path=str(clone_path),
                status=RepositoryStatus.CLONING
            )
            
            return metadata
            
        except GitCommandError as e:
            error_msg = f"Git clone failed: {str(e)}"
            logger.error(error_msg)
            
            # Clean up partial clone if exists
            if 'clone_path' in locals() and clone_path.exists():
                shutil.rmtree(clone_path)
            
            # Provide more specific error messages
            if "Repository not found" in str(e):
                raise ValueError("Repository not found. It may be private or doesn't exist.")
            elif "Authentication failed" in str(e):
                raise ValueError("Authentication required. Repository may be private.")
            else:
                raise GitCommandError(error_msg, e.status, e.stderr)
        
        except Exception as e:
            error_msg = f"Unexpected error during clone: {str(e)}"
            logger.error(error_msg)
            
            # Clean up if clone path was created
            if 'clone_path' in locals() and clone_path.exists():
                shutil.rmtree(clone_path)
            
            raise Exception(error_msg)
    
    def cleanup_repository(self, repo_id: str) -> bool:
        """
        Remove a cloned repository from disk
        
        Args:
            repo_id: Repository ID to clean up
            
        Returns:
            True if successful, False otherwise
        """
        try:
            clone_path = self.get_clone_path(repo_id)
            
            if not clone_path.exists():
                logger.warning(f"Repository {repo_id} not found at {clone_path}")
                return False
            
            logger.info(f"Cleaning up repository: {repo_id}")
            shutil.rmtree(clone_path)
            logger.success(f"Repository cleaned up: {repo_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to cleanup repository {repo_id}: {str(e)}")
            return False
    
    def get_repository_size(self, repo_id: str) -> int:
        """
        Get the size of a cloned repository in bytes
        
        Args:
            repo_id: Repository ID
            
        Returns:
            Size in bytes, or 0 if not found
        """
        try:
            clone_path = self.get_clone_path(repo_id)
            
            if not clone_path.exists():
                return 0
            
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(clone_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
            
            return total_size
            
        except Exception as e:
            logger.error(f"Failed to get repository size for {repo_id}: {str(e)}")
            return 0
    
    def list_cloned_repositories(self) -> list[str]:
        """
        List all cloned repository IDs
        
        Returns:
            List of repository IDs
        """
        try:
            if not self.storage_path.exists():
                return []
            
            return [
                d.name for d in self.storage_path.iterdir()
                if d.is_dir() and not d.name.startswith('.')
            ]
            
        except Exception as e:
            logger.error(f"Failed to list repositories: {str(e)}")
            return []


# Made with Bob