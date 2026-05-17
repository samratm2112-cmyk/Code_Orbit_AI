"""
FAISS Vector Store
Manages vector storage and similarity search using FAISS
"""

import os
import pickle
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
import numpy as np
import faiss

from shared.logger import logger
from shared.config import settings
from backend.models.chat import CodeChunk, VectorStoreInfo


class VectorStore:
    """
    FAISS-based vector store for code embeddings
    
    Features:
    - Persistent storage
    - Similarity search
    - Repository-specific indexes
    - Metadata management
    """
    
    def __init__(self, repo_id: str):
        """
        Initialize vector store for a repository
        
        Args:
            repo_id: Repository ID
        """
        self.repo_id = repo_id
        self.dimension = settings.embedding_dimension
        
        # Paths
        self.store_dir = settings.vector_store_path / repo_id
        self.store_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_path = self.store_dir / "index.faiss"
        self.metadata_path = self.store_dir / "metadata.pkl"
        self.info_path = self.store_dir / "info.pkl"
        
        # Initialize
        self.index: Optional[faiss.Index] = None
        self.chunks: List[CodeChunk] = []
        self.info: Dict[str, Any] = {}
        
        logger.info(f"VectorStore initialized for repo: {repo_id}")
    
    def create_index(
        self,
        chunks: List[CodeChunk],
        embeddings: List[np.ndarray]
    ):
        """
        Create FAISS index from chunks and embeddings
        
        Args:
            chunks: List of code chunks
            embeddings: List of embedding vectors
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        logger.info(f"Creating FAISS index with {len(chunks)} vectors")
        
        # Convert embeddings to numpy array and detect dimension dynamically
        embeddings_array = np.array(embeddings).astype('float32')
        if embeddings_array.ndim != 2:
            raise ValueError("Embeddings must be a 2D array of vectors")
        self.dimension = int(embeddings_array.shape[1])

        # Create FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)
        
        # Add vectors to index
        self.index.add(embeddings_array)
        
        # Store chunks
        self.chunks = chunks
        
        # Store info
        self.info = {
            'repo_id': self.repo_id,
            'total_vectors': len(chunks),
            'dimension': self.dimension,
            'created_at': datetime.utcnow(),
            'last_updated': datetime.utcnow()
        }
        
        logger.success(f"FAISS index created with {len(chunks)} vectors")
    
    def save(self):
        """Save index and metadata to disk"""
        if self.index is None:
            raise ValueError("No index to save")
        
        logger.info(f"Saving vector store to {self.store_dir}")
        
        # Save FAISS index
        faiss.write_index(self.index, str(self.index_path))
        
        # Save metadata (chunks)
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.chunks, f)
        
        # Save info
        with open(self.info_path, 'wb') as f:
            pickle.dump(self.info, f)
        
        logger.success(f"Vector store saved successfully")
    
    def load(self) -> bool:
        """
        Load index and metadata from disk
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if not self.exists():
            logger.warning(f"Vector store does not exist for repo: {self.repo_id}")
            return False
        
        try:
            logger.info(f"Loading vector store from {self.store_dir}")
            
            # Load FAISS index
            self.index = faiss.read_index(str(self.index_path))
            
            # Load metadata
            with open(self.metadata_path, 'rb') as f:
                self.chunks = pickle.load(f)
            
            # Load info
            with open(self.info_path, 'rb') as f:
                self.info = pickle.load(f)
            
            logger.success(f"Vector store loaded: {len(self.chunks)} vectors")
            return True
            
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            return False
    
    def exists(self) -> bool:
        """Check if vector store exists on disk"""
        return (
            self.index_path.exists() and
            self.metadata_path.exists() and
            self.info_path.exists()
        )
    
    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 5
    ) -> List[Tuple[CodeChunk, float]]:
        """
        Search for similar code chunks
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of (chunk, distance) tuples
        """
        if self.index is None:
            raise ValueError("Index not loaded. Call load() first.")
        
        # Ensure query is 2D array
        query_array = np.array([query_embedding]).astype('float32')
        
        # Search
        distances, indices = self.index.search(query_array, k)
        
        # Get results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.chunks):
                chunk = self.chunks[idx]
                # Convert L2 distance to similarity score (0-1)
                similarity = 1 / (1 + dist)
                results.append((chunk, float(similarity)))
        
        logger.debug(f"Found {len(results)} similar chunks")
        return results
    
    def get_info(self) -> VectorStoreInfo:
        """
        Get vector store information
        
        Returns:
            VectorStoreInfo object
        """
        if not self.exists():
            return VectorStoreInfo(
                repo_id=self.repo_id,
                exists=False,
                total_vectors=0,
                dimension=self.dimension
            )
        
        # Load info if not already loaded
        if not self.info and self.info_path.exists():
            with open(self.info_path, 'rb') as f:
                self.info = pickle.load(f)
        
        return VectorStoreInfo(
            repo_id=self.repo_id,
            exists=True,
            total_vectors=self.info.get('total_vectors', 0),
            dimension=self.info.get('dimension', self.dimension),
            created_at=self.info.get('created_at'),
            last_updated=self.info.get('last_updated'),
            index_path=str(self.index_path)
        )
    
    def delete(self):
        """Delete vector store from disk"""
        try:
            if self.store_dir.exists():
                import shutil
                shutil.rmtree(self.store_dir)
                logger.info(f"Vector store deleted for repo: {self.repo_id}")
                return True
        except Exception as e:
            logger.error(f"Error deleting vector store: {str(e)}")
            return False
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[CodeChunk]:
        """
        Get chunk by ID
        
        Args:
            chunk_id: Chunk ID
            
        Returns:
            CodeChunk or None
        """
        for chunk in self.chunks:
            if chunk.metadata.chunk_id == chunk_id:
                return chunk
        return None
    
    def get_chunks_by_file(self, file_path: str) -> List[CodeChunk]:
        """
        Get all chunks from a specific file
        
        Args:
            file_path: File path
            
        Returns:
            List of chunks from that file
        """
        return [
            chunk for chunk in self.chunks
            if chunk.metadata.file_path == file_path
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get vector store statistics
        
        Returns:
            Statistics dictionary
        """
        if not self.chunks:
            return {
                'total_chunks': 0,
                'total_files': 0,
                'languages': {},
                'avg_chunk_size': 0
            }
        
        # Count files
        files = set(chunk.metadata.file_path for chunk in self.chunks)
        
        # Count languages
        languages = {}
        for chunk in self.chunks:
            lang = chunk.metadata.language or 'Unknown'
            languages[lang] = languages.get(lang, 0) + 1
        
        # Average chunk size
        total_size = sum(len(chunk.content) for chunk in self.chunks)
        avg_size = total_size / len(self.chunks) if self.chunks else 0
        
        return {
            'total_chunks': len(self.chunks),
            'total_files': len(files),
            'languages': languages,
            'avg_chunk_size': int(avg_size),
            'dimension': self.dimension
        }


class VectorStoreManager:
    """
    Manager for multiple vector stores
    """
    
    def __init__(self):
        """Initialize vector store manager"""
        self.stores: Dict[str, VectorStore] = {}
        logger.info("VectorStoreManager initialized")
    
    def get_store(self, repo_id: str) -> VectorStore:
        """
        Get or create vector store for a repository
        
        Args:
            repo_id: Repository ID
            
        Returns:
            VectorStore instance
        """
        if repo_id not in self.stores:
            self.stores[repo_id] = VectorStore(repo_id)
        return self.stores[repo_id]
    
    def list_stores(self) -> List[str]:
        """
        List all available vector stores
        
        Returns:
            List of repository IDs
        """
        store_dir = settings.vector_store_path
        if not store_dir.exists():
            return []
        
        return [
            d.name for d in store_dir.iterdir()
            if d.is_dir() and (d / "index.faiss").exists()
        ]
    
    def delete_store(self, repo_id: str) -> bool:
        """
        Delete a vector store
        
        Args:
            repo_id: Repository ID
            
        Returns:
            True if deleted successfully
        """
        store = self.get_store(repo_id)
        success = store.delete()
        
        if success and repo_id in self.stores:
            del self.stores[repo_id]
        
        return success


# Global instance
vector_store_manager = VectorStoreManager()


# Made with Bob