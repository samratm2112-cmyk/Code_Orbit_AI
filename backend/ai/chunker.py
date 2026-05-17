"""
Intelligent Code Chunking System
Splits repository files into meaningful chunks for embedding generation
"""

import hashlib
from typing import List, Optional
from pathlib import Path

from shared.logger import logger
from shared.config import settings
from backend.models.chat import CodeChunk, ChunkMetadata
from backend.models.repository import FileMetadata


class CodeChunker:
    """
    Intelligent code chunking system
    
    Features:
    - Smart chunking by code structure
    - Preserves file context
    - Configurable chunk size and overlap
    - Language-aware splitting
    - Metadata preservation
    """
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        max_chunk_size: int = 2000
    ):
        """
        Initialize code chunker
        
        Args:
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks in characters
            max_chunk_size: Maximum chunk size in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_chunk_size = max_chunk_size
        
        logger.info(f"CodeChunker initialized: size={chunk_size}, overlap={chunk_overlap}")
    
    def chunk_file(
        self,
        file_metadata: FileMetadata,
        repo_id: str
    ) -> List[CodeChunk]:
        """
        Chunk a single file into meaningful pieces
        
        Args:
            file_metadata: File metadata with content
            repo_id: Repository ID
            
        Returns:
            List of code chunks
        """
        if not file_metadata.content:
            logger.warning(f"No content for file: {file_metadata.path}")
            return []
        
        content = file_metadata.content
        
        # Skip if content is too small
        if len(content) < 100:
            logger.debug(f"Skipping small file: {file_metadata.path}")
            return []
        
        # Choose chunking strategy based on file type
        if file_metadata.extension in ['.md', '.txt', '.rst']:
            chunks = self._chunk_by_paragraphs(content)
        elif file_metadata.extension in ['.json', '.yaml', '.yml']:
            chunks = self._chunk_by_structure(content)
        else:
            # Code files - chunk by lines with overlap
            chunks = self._chunk_by_lines(content)
        
        # Create CodeChunk objects with metadata
        code_chunks = []
        total_chunks = len(chunks)
        
        for idx, (chunk_content, start_line, end_line) in enumerate(chunks):
            chunk_id = self._generate_chunk_id(repo_id, file_metadata.path, idx)
            
            metadata = ChunkMetadata(
                chunk_id=chunk_id,
                repo_id=repo_id,
                file_path=file_metadata.path,
                language=file_metadata.language,
                start_line=start_line,
                end_line=end_line,
                chunk_index=idx,
                total_chunks=total_chunks
            )
            
            code_chunk = CodeChunk(
                content=chunk_content,
                metadata=metadata
            )
            
            code_chunks.append(code_chunk)
        
        logger.debug(f"Chunked {file_metadata.path} into {len(code_chunks)} chunks")
        return code_chunks
    
    def chunk_repository(
        self,
        files: List[FileMetadata],
        repo_id: str,
        max_files: Optional[int] = None
    ) -> List[CodeChunk]:
        """
        Chunk all files in a repository
        
        Args:
            files: List of file metadata
            repo_id: Repository ID
            max_files: Maximum number of files to process
            
        Returns:
            List of all code chunks
        """
        all_chunks = []
        files_to_process = files[:max_files] if max_files else files
        
        logger.info(f"Chunking {len(files_to_process)} files for repo {repo_id}")
        
        for file_metadata in files_to_process:
            try:
                chunks = self.chunk_file(file_metadata, repo_id)
                all_chunks.extend(chunks)
            except Exception as e:
                logger.error(f"Error chunking file {file_metadata.path}: {str(e)}")
                continue
        
        logger.info(f"Generated {len(all_chunks)} total chunks for repo {repo_id}")
        return all_chunks
    
    def _chunk_by_lines(self, content: str) -> List[tuple]:
        """
        Chunk content by lines with overlap
        
        Args:
            content: File content
            
        Returns:
            List of (chunk_content, start_line, end_line) tuples
        """
        lines = content.split('\n')
        chunks = []
        
        # Calculate lines per chunk
        avg_line_length = len(content) / len(lines) if lines else 80
        lines_per_chunk = max(10, int(self.chunk_size / avg_line_length))
        overlap_lines = max(2, int(self.chunk_overlap / avg_line_length))
        
        start = 0
        while start < len(lines):
            end = min(start + lines_per_chunk, len(lines))
            
            chunk_lines = lines[start:end]
            chunk_content = '\n'.join(chunk_lines)
            
            # Only add if chunk has meaningful content
            if len(chunk_content.strip()) > 50:
                chunks.append((
                    chunk_content,
                    start + 1,  # 1-based line numbers
                    end
                ))
            
            # Move start with overlap
            start = end - overlap_lines if end < len(lines) else end
            
            # Prevent infinite loop
            if start >= len(lines):
                break
        
        return chunks
    
    def _chunk_by_paragraphs(self, content: str) -> List[tuple]:
        """
        Chunk markdown/text by paragraphs
        
        Args:
            content: File content
            
        Returns:
            List of (chunk_content, start_line, end_line) tuples
        """
        # Split by double newlines (paragraphs)
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = []
        current_size = 0
        start_line = 1
        current_line = 1
        
        for para in paragraphs:
            para_size = len(para)
            para_lines = para.count('\n') + 1
            
            if current_size + para_size > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_content = '\n\n'.join(current_chunk)
                chunks.append((chunk_content, start_line, current_line - 1))
                
                # Start new chunk with overlap
                if len(current_chunk) > 1:
                    current_chunk = [current_chunk[-1], para]
                    current_size = len(current_chunk[-2]) + para_size
                    start_line = current_line - current_chunk[-2].count('\n') - 1
                else:
                    current_chunk = [para]
                    current_size = para_size
                    start_line = current_line
            else:
                current_chunk.append(para)
                current_size += para_size
            
            current_line += para_lines + 1  # +1 for the blank line
        
        # Add remaining chunk
        if current_chunk:
            chunk_content = '\n\n'.join(current_chunk)
            chunks.append((chunk_content, start_line, current_line - 1))
        
        return chunks
    
    def _chunk_by_structure(self, content: str) -> List[tuple]:
        """
        Chunk structured files (JSON, YAML) more carefully
        
        Args:
            content: File content
            
        Returns:
            List of (chunk_content, start_line, end_line) tuples
        """
        # For structured files, use line-based chunking but with larger chunks
        lines = content.split('\n')
        
        if len(content) <= self.max_chunk_size:
            # Keep small structured files whole
            return [(content, 1, len(lines))]
        
        # Otherwise chunk by lines
        return self._chunk_by_lines(content)
    
    def _generate_chunk_id(self, repo_id: str, file_path: str, chunk_index: int) -> str:
        """
        Generate unique chunk ID
        
        Args:
            repo_id: Repository ID
            file_path: File path
            chunk_index: Chunk index
            
        Returns:
            Unique chunk ID
        """
        # Create a hash of the file path for shorter IDs
        path_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
        return f"{repo_id}_{path_hash}_chunk{chunk_index}"
    
    def get_chunk_context(self, chunk: CodeChunk, window: int = 5) -> str:
        """
        Get context information for a chunk
        
        Args:
            chunk: Code chunk
            window: Number of lines before/after to mention
            
        Returns:
            Context string
        """
        context_parts = [
            f"File: {chunk.metadata.file_path}",
            f"Lines: {chunk.metadata.start_line}-{chunk.metadata.end_line}",
        ]
        
        if chunk.metadata.language:
            context_parts.append(f"Language: {chunk.metadata.language}")
        
        context_parts.append(f"Chunk {chunk.metadata.chunk_index + 1} of {chunk.metadata.total_chunks}")
        
        return " | ".join(context_parts)
    
    def estimate_chunks(self, files: List[FileMetadata]) -> int:
        """
        Estimate number of chunks that will be generated
        
        Args:
            files: List of file metadata
            
        Returns:
            Estimated chunk count
        """
        total_chars = sum(len(f.content or '') for f in files)
        estimated = int(total_chars / self.chunk_size * 1.2)  # 20% buffer
        return max(1, estimated)


# Made with Bob