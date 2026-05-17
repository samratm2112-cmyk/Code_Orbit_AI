from __future__ import annotations
"""
Local Embeddings Service
Generates vector embeddings for code chunks using sentence-transformers.
NO OpenAI dependency - works completely offline.
"""

import asyncio
from typing import List, Optional, Dict, Any
import numpy as np

from shared.logger import logger
from shared.config import settings
from backend.models.chat import CodeChunk, EmbeddingProgress, EmbeddingStatus


class EmbeddingsService:
    """
    Local-only embeddings service using sentence-transformers
    
    Features:
    - 100% offline operation
    - sentence-transformers embeddings
    - Lazy model loading
    - Asynchronous batch processing
    - Progress tracking
    """
    
    def __init__(self):
        """Initialize local embeddings service"""
        self.model_name = "all-MiniLM-L6-v2"
        self.dimension = 384  # Default for all-MiniLM-L6-v2
        self.batch_size = min(settings.max_embeddings_per_batch, 100)
        self._local_model: Optional[Any] = None
        self._model_available: Optional[bool] = None
        self.progress_tracker: Dict[str, EmbeddingProgress] = {}
        logger.info("Local EmbeddingsService initialized")
    
    def _load_local_model(self):
        """Load the sentence-transformers model lazily"""
        if self._local_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading local embedding model: {self.model_name}")
                self._local_model = SentenceTransformer(self.model_name, device='cpu')
                self.dimension = self._local_model.get_sentence_embedding_dimension()
                logger.success(f"Local embedding model loaded successfully (dimension: {self.dimension})")
            except ImportError as exc:
                logger.error("sentence-transformers not installed!")
                raise ImportError(
                    "sentence-transformers is required for local embeddings. "
                    "Install it with: pip install sentence-transformers transformers torch"
                ) from exc
            except Exception as exc:
                logger.error(f"Failed to load local model: {exc}")
                raise RuntimeError(f"Failed to load embedding model: {exc}") from exc
        
        return self._local_model

    def is_available(self) -> bool:
        """Check if local embeddings service is available"""
        if self._model_available is not None:
            return self._model_available

        try:
            import sentence_transformers  # noqa: F401
            self._model_available = True
            logger.info("Local embeddings available")
        except ImportError:
            logger.error("sentence-transformers not installed - AI features unavailable")
            self._model_available = False
        except Exception as exc:
            logger.error(f"Local embeddings check failed: {exc}")
            self._model_available = False
        
        return self._model_available
    
    async def generate_embeddings(
        self,
        chunks: List[CodeChunk],
        repo_id: str,
        progress_callback: Optional[callable] = None
    ) -> List[np.ndarray]:
        """
        Generate embeddings for code chunks using local model
        """
        logger.info(f"Generating local embeddings for {len(chunks)} chunks (repo: {repo_id})")
        
        progress = EmbeddingProgress(
            repo_id=repo_id,
            status=EmbeddingStatus.IN_PROGRESS,
            total_chunks=len(chunks),
            processed_chunks=0,
            progress_percentage=0.0
        )
        self.progress_tracker[repo_id] = progress
        
        try:
            # Load local model
            model = self._load_local_model()
            embeddings: List[np.ndarray] = []

            # Process in batches
            for i in range(0, len(chunks), self.batch_size):
                batch = chunks[i:i + self.batch_size]
                texts = []
                for chunk in batch:
                    context = f"File: {chunk.metadata.file_path}\n"
                    if chunk.metadata.language:
                        context += f"Language: {chunk.metadata.language}\n"
                    context += f"\n{chunk.content}"
                    texts.append(context)

                # Generate embeddings
                batch_embeddings = await asyncio.get_running_loop().run_in_executor(
                    None,
                    lambda texts=texts: model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
                )

                embeddings.extend([np.array(vec, dtype=np.float32) for vec in batch_embeddings])
                
                progress.processed_chunks = min(i + self.batch_size, len(chunks))
                progress.progress_percentage = (progress.processed_chunks / progress.total_chunks) * 100
                if progress_callback:
                    progress_callback(progress)
                
                logger.info(f"Progress: {progress.processed_chunks}/{progress.total_chunks} chunks")

            progress.status = EmbeddingStatus.COMPLETED
            progress.progress_percentage = 100.0
            logger.success(f"Generated {len(embeddings)} local embeddings for repo {repo_id}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating local embeddings: {str(e)}")
            progress.status = EmbeddingStatus.FAILED
            progress.error_message = str(e)
            raise
    
    async def generate_query_embedding_async(self, query: str) -> np.ndarray:
        """
        Generate embedding for a query using local model
        """
        try:
            model = self._load_local_model()
            embedding = await asyncio.get_running_loop().run_in_executor(
                None,
                lambda: model.encode(query, convert_to_numpy=True, show_progress_bar=False)
            )
            return np.array(embedding, dtype=np.float32)
            
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise
    
    def get_progress(self, repo_id: str) -> Optional[EmbeddingProgress]:
        """Get embedding progress for a repository"""
        return self.progress_tracker.get(repo_id)
    
    def clear_progress(self, repo_id: str):
        """Clear progress tracking for a repository"""
        if repo_id in self.progress_tracker:
            del self.progress_tracker[repo_id]
    
    def estimate_cost(self, num_chunks: int) -> Dict[str, Any]:
        """Estimate cost (always free for local embeddings)"""
        return {
            "num_chunks": num_chunks,
            "estimated_cost_usd": 0.0,
            "model": self.model_name,
            "note": "Local embeddings are generated offline at no cost"
        }
    
    def get_embedding_dimension(self) -> int:
        """Get embedding dimension"""
        return self.dimension


# Global instance
embeddings_service = EmbeddingsService()


# Made with Bob