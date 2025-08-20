"""
Abstract interface for vector storage and search.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from .schemas import DocumentChunk


class VectorStore(ABC):
    """Abstract base class for vector storage implementations."""
    
    @abstractmethod
    def add_documents(self, chunks: List[DocumentChunk], embeddings: List[List[float]]) -> None:
        """
        Add document chunks with their embeddings to the store.
        
        Args:
            chunks: List of document chunks
            embeddings: List of embedding vectors corresponding to chunks
        """
        pass
    
    @abstractmethod
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[DocumentChunk]:
        """
        Search for similar documents using cosine similarity.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of top results to return
            
        Returns:
            List of most similar document chunks
        """
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with store statistics
        """
        pass
    
    @abstractmethod
    def save(self, path: str) -> None:
        """
        Save the vector store to disk.
        
        Args:
            path: Directory path to save the store
        """
        pass
    
    @abstractmethod
    def load(self, path: str) -> None:
        """
        Load the vector store from disk.
        
        Args:
            path: Directory path to load the store from
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all data from the store."""
        pass
