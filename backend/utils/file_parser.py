"""
File Parser Utility
Handles parsing and extraction of various file types
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import chardet

from shared.logger import logger
from shared.config import settings
from shared.constants import (
    LANGUAGE_EXTENSIONS,
    MAX_FILE_SIZE,
    IGNORE_PATTERNS
)
from backend.models.repository import FileMetadata


class FileParser:
    """
    Parser for extracting file content and metadata
    
    Features:
    - Read file contents safely
    - Handle encoding issues
    - Skip huge files
    - Return structured metadata
    - Support multiple file types
    """
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {
        '.py', '.js', '.jsx', '.ts', '.tsx',
        '.java', '.go', '.rs', '.cpp', '.c', '.h',
        '.rb', '.php', '.swift', '.kt',
        '.md', '.markdown', '.txt',
        '.json', '.yaml', '.yml', '.toml', '.xml',
        '.html', '.css', '.scss', '.sass', '.less',
        '.sh', '.bash', '.sql'
    }
    
    # Binary file extensions to skip
    BINARY_EXTENSIONS = {
        '.pyc', '.pyo', '.pyd', '.so', '.dll', '.dylib',
        '.exe', '.bin', '.dat', '.db', '.sqlite',
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico',
        '.pdf', '.zip', '.tar', '.gz', '.rar', '.7z',
        '.mp3', '.mp4', '.avi', '.mov', '.wav',
        '.ttf', '.otf', '.woff', '.woff2', '.eot'
    }
    
    def __init__(self, max_file_size: int = MAX_FILE_SIZE):
        """
        Initialize file parser
        
        Args:
            max_file_size: Maximum file size to process in bytes
        """
        self.max_file_size = max_file_size
        logger.info(f"FileParser initialized with max file size: {max_file_size} bytes")
    
    def should_parse_file(self, file_path: Path) -> bool:
        """
        Check if a file should be parsed
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file should be parsed, False otherwise
        """
        # Check if file exists
        if not file_path.exists() or not file_path.is_file():
            return False
        
        # Check file extension
        extension = file_path.suffix.lower()
        
        # Skip binary files
        if extension in self.BINARY_EXTENSIONS:
            return False
        
        # Only parse supported extensions
        if extension not in self.SUPPORTED_EXTENSIONS:
            return False
        
        # Check file size
        try:
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                logger.warning(f"Skipping large file: {file_path} ({file_size} bytes)")
                return False
        except Exception as e:
            logger.error(f"Error checking file size for {file_path}: {str(e)}")
            return False
        
        # Check ignore patterns
        file_name = file_path.name
        for pattern in IGNORE_PATTERNS:
            if pattern.replace('*', '') in file_name:
                return False
        
        return True
    
    def detect_encoding(self, file_path: Path) -> str:
        """
        Detect file encoding
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected encoding (default: utf-8)
        """
        try:
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                
                if encoding and result['confidence'] > 0.7:
                    return encoding
                
        except Exception as e:
            logger.warning(f"Error detecting encoding for {file_path}: {str(e)}")
        
        return 'utf-8'
    
    def read_file_content(self, file_path: Path) -> Optional[str]:
        """
        Read file content with encoding handling
        
        Args:
            file_path: Path to the file
            
        Returns:
            File content as string, or None if failed
        """
        # Try UTF-8 first
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        # Add detected encoding
        detected_encoding = self.detect_encoding(file_path)
        if detected_encoding and detected_encoding not in encodings:
            encodings.insert(0, detected_encoding)
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                    content = f.read()
                    return content
            except Exception as e:
                continue
        
        logger.error(f"Failed to read file with any encoding: {file_path}")
        return None
    
    def detect_language(self, file_path: Path) -> Optional[str]:
        """
        Detect programming language from file extension
        
        Args:
            file_path: Path to the file
            
        Returns:
            Language name or None
        """
        extension = file_path.suffix.lower()
        
        for language, extensions in LANGUAGE_EXTENSIONS.items():
            if extension in extensions:
                return language
        
        return None
    
    def count_lines(self, content: str) -> int:
        """
        Count number of lines in content
        
        Args:
            content: File content
            
        Returns:
            Number of lines
        """
        if not content:
            return 0
        return len(content.splitlines())
    
    def parse_file(
        self,
        file_path: Path,
        include_content: bool = True,
        relative_to: Optional[Path] = None
    ) -> Optional[FileMetadata]:
        """
        Parse a file and extract metadata
        
        Args:
            file_path: Path to the file
            include_content: Whether to include file content
            relative_to: Base path for relative path calculation
            
        Returns:
            FileMetadata object or None if parsing failed
        """
        try:
            # Check if file should be parsed
            if not self.should_parse_file(file_path):
                return None
            
            # Get file stats
            file_stats = file_path.stat()
            file_size = file_stats.st_size
            
            # Read content if requested
            content = None
            if include_content:
                content = self.read_file_content(file_path)
                if content is None:
                    logger.warning(f"Could not read content for: {file_path}")
            
            # Calculate relative path
            if relative_to:
                try:
                    relative_path = str(file_path.relative_to(relative_to))
                except ValueError:
                    relative_path = str(file_path)
            else:
                relative_path = str(file_path)
            
            # Detect language
            language = self.detect_language(file_path)
            
            # Count lines
            line_count = 0
            if content:
                line_count = self.count_lines(content)
            
            # Create metadata
            metadata = FileMetadata(
                path=relative_path,
                extension=file_path.suffix.lower(),
                size_bytes=file_size,
                line_count=line_count,
                language=language,
                content=content if include_content else None
            )
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {str(e)}")
            return None
    
    def parse_directory(
        self,
        directory: Path,
        include_content: bool = True,
        recursive: bool = True
    ) -> List[FileMetadata]:
        """
        Parse all files in a directory
        
        Args:
            directory: Directory path
            include_content: Whether to include file contents
            recursive: Whether to parse subdirectories
            
        Returns:
            List of FileMetadata objects
        """
        parsed_files = []
        
        try:
            if recursive:
                # Walk through all subdirectories
                for root, dirs, files in os.walk(directory):
                    root_path = Path(root)
                    
                    # Filter out ignored directories
                    dirs[:] = [d for d in dirs if not self._should_ignore_directory(d)]
                    
                    for file_name in files:
                        file_path = root_path / file_name
                        metadata = self.parse_file(
                            file_path,
                            include_content=include_content,
                            relative_to=directory
                        )
                        if metadata:
                            parsed_files.append(metadata)
            else:
                # Only parse files in the top-level directory
                for file_path in directory.iterdir():
                    if file_path.is_file():
                        metadata = self.parse_file(
                            file_path,
                            include_content=include_content,
                            relative_to=directory
                        )
                        if metadata:
                            parsed_files.append(metadata)
            
            logger.info(f"Parsed {len(parsed_files)} files from {directory}")
            
        except Exception as e:
            logger.error(f"Error parsing directory {directory}: {str(e)}")
        
        return parsed_files
    
    def _should_ignore_directory(self, dir_name: str) -> bool:
        """
        Check if a directory should be ignored
        
        Args:
            dir_name: Directory name
            
        Returns:
            True if should be ignored
        """
        from shared.constants import IGNORE_DIRECTORIES
        
        # Check exact matches
        if dir_name in IGNORE_DIRECTORIES:
            return True
        
        # Check if starts with dot (hidden directories)
        if dir_name.startswith('.'):
            return True
        
        return False
    
    def get_file_summary(self, files: List[FileMetadata]) -> Dict[str, Any]:
        """
        Generate summary statistics for parsed files
        
        Args:
            files: List of FileMetadata objects
            
        Returns:
            Dictionary with summary statistics
        """
        total_files = len(files)
        total_lines = sum(f.line_count for f in files)
        total_size = sum(f.size_bytes for f in files)
        
        # Count by language
        language_counts = {}
        for file in files:
            if file.language:
                language_counts[file.language] = language_counts.get(file.language, 0) + 1
        
        # Count by extension
        extension_counts = {}
        for file in files:
            extension_counts[file.extension] = extension_counts.get(file.extension, 0) + 1
        
        return {
            'total_files': total_files,
            'total_lines': total_lines,
            'total_size_bytes': total_size,
            'languages': language_counts,
            'extensions': extension_counts
        }


# Made with Bob