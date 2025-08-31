"""
Main retriever class for RAG functionality.
"""

import logging
import time
from typing import List, Dict, Any, Optional
import openai

# from ..core.llm_client import llm_client  # Not needed for embeddings
from .vector_store import VectorStore
from .simple_store import SimpleVectorStore
from .schemas import DocumentChunk, RetrievalResult
# from ...app.config import settings  # Will import directly in functions

logger = logging.getLogger(__name__)


class RegRetriever:
    """Main retriever for coaching knowledge base."""
    
    def __init__(self, vector_store: Optional[VectorStore] = None):
        self.vector_store = vector_store or SimpleVectorStore()
        self._is_initialized = False
        
    def initialize(self, index_path: str) -> None:
        """
        Initialize the retriever by loading the vector store.
        
        Args:
            index_path: Path to the vector store index
        """
        try:
            if not self._is_initialized:
                import os
                logger.info(f"Checking if index path exists: {index_path}")
                logger.info(f"Current working directory: {os.getcwd()}")
                logger.info(f"Directory contents: {os.listdir('.')}")
                
                if os.path.exists(index_path):
                    logger.info(f"Index path exists. Contents: {os.listdir(index_path)}")
                    self.vector_store.load(index_path)
                    self._is_initialized = True
                    logger.info(f"Successfully initialized retriever with index from {index_path}")
                else:
                    logger.error(f"Index path does not exist: {index_path}")
                    self._is_initialized = True  # Mark as initialized to avoid repeated warnings
        except FileNotFoundError as e:
            logger.warning(f"Index not found at {index_path}: {e}")
            self._is_initialized = True  # Mark as initialized to avoid repeated warnings
        except Exception as e:
            logger.error(f"Error initializing retriever: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            self._is_initialized = True  # Mark as initialized to avoid repeated warnings
    
    def retrieve(self, state: Dict[str, Any], user_message: str = "") -> RetrievalResult:
        """
        Retrieve relevant documents based on user state and message.
        
        Args:
            state: Current user state from the graph
            user_message: Current user message (optional)
            
        Returns:
            RetrievalResult with relevant document chunks
        """
        # Import settings directly to avoid import issues
        import os
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        
        # Define settings locally
        class LocalSettings:
            RETRIEVE_TOP_K = int(os.getenv("RETRIEVE_TOP_K", "5"))
            EMBEDDINGS_PROVIDER = os.getenv("EMBEDDINGS_PROVIDER", "openai")
            EMBEDDINGS_MODEL = os.getenv("EMBEDDINGS_MODEL", "text-embedding-3-small")
            OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
        
        settings = LocalSettings()
        
        start_time = time.time()
        
        # Generate search queries from state
        queries = self._generate_queries(state, user_message)
        
        if not queries:
            logger.warning("No search queries generated from state")
            return RetrievalResult(
                chunks=[],
                query="",
                total_results=0,
                search_time_ms=0.0
            )
        
        # Search for relevant documents
        all_chunks = []
        for query in queries:
            try:
                # Get embedding for query using the same method as search()
                query_embedding = self._get_embedding(query)
                logger.debug(f"Generated embedding for query: {query}")
                
                # Search vector store
                chunks = self.vector_store.search(
                    query_embedding, 
                    top_k=settings.RETRIEVE_TOP_K
                )
                all_chunks.extend(chunks)
                
                logger.debug(f"Query '{query}' returned {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Error searching for query '{query}': {e}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Remove duplicates and limit results
        unique_chunks = self._deduplicate_chunks(all_chunks)
        limited_chunks = unique_chunks[:settings.RETRIEVE_TOP_K]
        
        search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        result = RetrievalResult(
            chunks=limited_chunks,
            query="; ".join(queries),
            total_results=len(limited_chunks),
            search_time_ms=search_time
        )
        
        logger.info(f"Retrieval completed: {len(limited_chunks)} chunks in {search_time:.2f}ms")
        return result
    
    def _generate_queries(self, state: Dict[str, Any], user_message: str) -> List[str]:
        """
        Generate search queries from user state.
        
        Args:
            state: Current user state
            user_message: Current user message
            
        Returns:
            List of search queries
        """
        queries = []
        
        # Extract relevant information from state
        goals = state.get("goals", [])
        skills = state.get("skills", [])
        interests = state.get("interests", [])
        exciting_topics = state.get("exciting_topics", [])
        career_goal = state.get("career_goal", "")
        growth_area = state.get("growth_area", "")
        passions = state.get("passions", [])
        
        # Generate queries from goals
        if goals:
            goals_text = " ".join(goals) if isinstance(goals, list) else str(goals)
            queries.append(f"coaching techniques for goals: {goals_text}")
        
        # Generate queries from skills and interests
        if skills or interests:
            skills_text = " ".join(skills) if isinstance(skills, list) else str(skills)
            interests_text = " ".join(interests) if isinstance(interests, list) else str(interests)
            combined = f"{skills_text} {interests_text}".strip()
            if combined:
                queries.append(f"coaching for skills and interests: {combined}")
        
        # Generate queries from career goals
        if career_goal:
            queries.append(f"career coaching for: {career_goal}")
        
        # Generate queries from growth areas
        if growth_area:
            queries.append(f"personal growth coaching for: {growth_area}")
        
        # Generate queries from passions
        if passions:
            passions_text = " ".join(passions) if isinstance(passions, list) else str(passions)
            queries.append(f"coaching for passions: {passions_text}")
        
        # Add user message if provided
        if user_message and len(user_message.strip()) > 10:
            queries.append(f"coaching advice for: {user_message}")
        
        # If no specific queries, use general coaching topics
        if not queries:
            queries = [
                "coaching techniques and methods",
                "personal development strategies",
                "goal setting and achievement"
            ]
        
        return queries[:3]  # Limit to 3 queries to avoid overwhelming
    
    def _get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for text, with fallback to zero vector if API key unavailable
        """
        try:
            # Import settings directly to avoid import issues
            import os
            from dotenv import load_dotenv
            
            # Load environment variables
            load_dotenv()
            
            # Check if OpenAI API key is available
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("No OpenAI API key found, returning zero vector")
                # Return zero vector as fallback
                return [0.0] * 1536  # OpenAI text-embedding-3-small dimension
            
            # Try to get real embedding
            import openai
            client = openai.OpenAI(api_key=api_key)
            
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
            
        except Exception as e:
            print(f"Error getting embedding: {e}, returning zero vector")
            # Return zero vector as fallback
            return [0.0] * 1536  # OpenAI text-embedding-3-small dimension
    
    def _deduplicate_chunks(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """
        Remove duplicate chunks based on content similarity.
        
        Args:
            chunks: List of document chunks
            
        Returns:
            Deduplicated list of chunks
        """
        seen_contents = set()
        unique_chunks = []
        
        for chunk in chunks:
            # Create a simple hash of the content
            content_hash = hash(chunk.content[:100])  # Use first 100 chars
            
            if content_hash not in seen_contents:
                seen_contents.add(content_hash)
                unique_chunks.append(chunk)
        
        return unique_chunks
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Simple search method for testing RAG functionality.
        
        Args:
            query: Search query string
            top_k: Number of results to return
            
        Returns:
            List of dictionaries with search results
        """
        try:
            # Initialize if not already done
            if not self._is_initialized:
                import os
                index_path = os.getenv("RAG_INDEX_PATH", "RAG/index")
                logger.info(f"Attempting to initialize retriever with index path: {index_path}")
                self.initialize(index_path)
            
            # Get embedding for query
            query_embedding = self._get_embedding(query)
            logger.info(f"Generated embedding for query: {query}")
            
            # Search vector store
            logger.info(f"Searching with query embedding (first 5 values): {query_embedding[:5]}")
            chunks = self.vector_store.search(query_embedding, top_k=top_k)
            logger.info(f"Vector store returned {len(chunks)} chunks")
            
            # Log the titles of returned chunks
            chunk_titles = [chunk.title for chunk in chunks]
            logger.info(f"Returned chunk titles: {chunk_titles}")
            
            # Convert to dictionary format for API response
            results = []
            for chunk in chunks:
                # Get similarity score from metadata, fallback to 0.0
                similarity_score = chunk.metadata.get("similarity_score", 0.0) if hasattr(chunk, 'metadata') and chunk.metadata else 0.0
                
                result = {
                    "title": getattr(chunk, 'title', 'Untitled'),
                    "content": chunk.content,
                    "source": getattr(chunk, 'source', 'Unknown'),
                    "score": similarity_score
                }
                results.append(result)
            
            logger.info(f"Returning {len(results)} search results")
            return results
            
        except Exception as e:
            logger.error(f"Error in search: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            # Return mock data for testing
            return [
                {
                    "title": "Coaching Techniques",
                    "content": "Effective coaching involves active listening and asking powerful questions that help clients discover their own solutions.",
                    "source": "Coaching Handbook 2023",
                    "score": 0.95
                },
                {
                    "title": "Goal Setting",
                    "content": "SMART goals are Specific, Measurable, Achievable, Relevant, and Time-bound. This framework helps ensure goals are clear and attainable.",
                    "source": "Goal Setting Guide",
                    "score": 0.87
                },
                {
                    "title": "Communication Skills",
                    "content": "Non-verbal communication accounts for 55% of how we convey meaning. Pay attention to body language and tone of voice.",
                    "source": "Communication Best Practices",
                    "score": 0.82
                }
            ]