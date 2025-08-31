"""
Simple vector store implementation using numpy and cosine similarity.
"""

import os
import json
import pickle
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from pathlib import Path

from .vector_store import VectorStore
from .schemas import DocumentChunk

logger = logging.getLogger(__name__)


class SimpleVectorStore(VectorStore):
    """Simple vector store using numpy arrays and cosine similarity."""
    
    def __init__(self):
        self.chunks: List[DocumentChunk] = []
        self.embeddings: List[List[float]] = []
        self._embeddings_array: Optional[np.ndarray] = None
        
    def add_documents(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> None:
        """Add document chunks with their embeddings to the store."""
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
            
        # Add new chunks and embeddings
        self.chunks.extend(chunks)
        self.embeddings.extend(embeddings)
        
        # Update numpy array for faster computation
        self._embeddings_array = np.array(self.embeddings, dtype=np.float32)
        
        logger.info(f"Added {len(chunks)} documents to vector store. Total: {len(self.chunks)}")
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[DocumentChunk]:
        """Search for similar documents using cosine similarity."""
        if not self.chunks:
            logger.warning("Vector store is empty. Returning empty results.")
            return []
            
        if self._embeddings_array is None:
            self._embeddings_array = np.array(self.embeddings, dtype=np.float32)
        
        # Convert query to numpy array
        query_array = np.array(query_embedding, dtype=np.float32).reshape(1, -1)
        
        # Debug: check array shapes
        logger.info(f"Query array shape: {query_array.shape}")
        logger.info(f"Embeddings array shape: {self._embeddings_array.shape}")
        
        # Ensure embeddings array has correct shape (num_docs, embedding_dim)
        if len(self._embeddings_array.shape) == 1:
            # If 1D, reshape to 2D
            num_chunks = len(self.chunks)
            total_elements = self._embeddings_array.size
            
            if num_chunks > 0 and total_elements > 0:
                embedding_dim = total_elements // num_chunks
                if embedding_dim > 0 and embedding_dim * num_chunks == total_elements:
                    logger.info(f"Reshaping 1D embeddings array to ({num_chunks}, {embedding_dim})")
                    self._embeddings_array = self._embeddings_array.reshape(num_chunks, embedding_dim)
                else:
                    logger.error(f"Cannot reshape: total_elements={total_elements}, num_chunks={num_chunks}, embedding_dim={embedding_dim}")
                    raise ValueError(f"Invalid embeddings array shape: cannot reshape {self._embeddings_array.shape} to 2D")
            else:
                logger.error(f"Invalid dimensions: num_chunks={num_chunks}, total_elements={total_elements}")
                raise ValueError(f"Invalid embeddings array: num_chunks={num_chunks}, total_elements={total_elements}")
        
        # Normalize vectors for cosine similarity
        query_norm = query_array / np.linalg.norm(query_array, axis=1, keepdims=True)
        embeddings_norm = self._embeddings_array / np.linalg.norm(self._embeddings_array, axis=1, keepdims=True)
        
        # Compute cosine similarities
        similarities = np.dot(embeddings_norm, query_norm.T).flatten()
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Log similarities for debugging
        logger.info(f"Similarities for top {top_k} results: {similarities[top_indices]}")
        logger.info(f"Top indices: {top_indices}")
        
        # Return corresponding chunks with scores
        results = []
        for i, idx in enumerate(top_indices):
            chunk = self.chunks[idx]
            # Add similarity score to chunk metadata
            chunk.metadata["similarity_score"] = float(similarities[idx])
            results.append(chunk)
        
        # Log the titles of returned chunks
        result_titles = [chunk.title for chunk in results]
        logger.info(f"Returned chunk titles: {result_titles}")
        
        logger.debug(f"Search returned {len(results)} results with similarities: {similarities[top_indices]}")
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            "total_documents": len(self.chunks),
            "total_embeddings": len(self.embeddings),
            "embedding_dimension": len(self.embeddings[0]) if self.embeddings else 0,
            "store_type": "SimpleVectorStore"
        }
    
    def save(self, path: str) -> None:
        """Save the vector store to disk."""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        # Save chunks as JSON
        chunks_file = path / "chunks.json"
        chunks_data = [chunk.dict() for chunk in self.chunks]
        
        # Custom JSON encoder to handle datetime objects
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj):
                if hasattr(obj, 'isoformat'):
                    return obj.isoformat()
                return super().default(obj)
        
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
        
        # Save embeddings as numpy array
        embeddings_file = path / "embeddings.npy"
        if self.embeddings:
            np.save(embeddings_file, np.array(self.embeddings))
        
        # Save metadata
        metadata = {
            "version": "1.0",
            "store_type": "SimpleVectorStore",
            "total_documents": len(self.chunks),
            "embedding_dimension": len(self.embeddings[0]) if self.embeddings else 0
        }
        
        metadata_file = path / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved vector store to {path}")
    
    def load(self, path: str) -> None:
        """Load the vector store from disk."""
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Vector store path does not exist: {path}")
        
        # Load chunks
        chunks_file = path / "chunks.json"
        if chunks_file.exists():
            with open(chunks_file, 'r', encoding='utf-8') as f:
                chunks_data = json.load(f)
            self.chunks = [DocumentChunk(**chunk_data) for chunk_data in chunks_data]
        
        # Load embeddings
        embeddings_file = path / "embeddings.npy"
        if embeddings_file.exists():
            embeddings_array = np.load(embeddings_file)
            logger.info(f"Loaded embeddings array shape: {embeddings_array.shape}")
            
            # Ensure embeddings array is 2D
            if len(embeddings_array.shape) == 1:
                num_chunks = len(self.chunks)
                total_elements = embeddings_array.size
                if num_chunks > 0 and total_elements > 0:
                    embedding_dim = total_elements // num_chunks
                    if embedding_dim > 0 and embedding_dim * num_chunks == total_elements:
                        embeddings_array = embeddings_array.reshape(num_chunks, embedding_dim)
                        logger.info(f"Reshaped embeddings array to: {embeddings_array.shape}")
                    else:
                        logger.error(f"Cannot reshape embeddings: {embeddings_array.shape}")
                        raise ValueError(f"Invalid embeddings array shape")
            
            self.embeddings = embeddings_array.tolist()
            self._embeddings_array = embeddings_array
        
        logger.info(f"Loaded vector store from {path}: {len(self.chunks)} documents")
    
    def clear(self) -> None:
        """Clear all data from the store."""
        self.chunks.clear()
        self.embeddings.clear()
        self._embeddings_array = None
        logger.info("Cleared vector store")
