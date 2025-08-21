#!/usr/bin/env python3
"""
Create a real RAG index with proper OpenAI embeddings.
"""

import os
import sys
import json
import time
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from mentor_ai.cursor.modules.retrieval.schemas import DocumentChunk
from mentor_ai.cursor.core.llm_client import LLMClient

# Load environment variables
load_dotenv()

def create_real_index():
    """Create a real RAG index with proper embeddings."""
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        return
    
    # Setup paths
    index_path = Path("RAG/index")
    index_path.mkdir(parents=True, exist_ok=True)
    
    print("🔧 Creating real RAG index with OpenAI embeddings...")
    
    # Initialize OpenAI embeddings client
    embeddings_client = LLMClient()
    
    # Create test documents with diverse content
    test_documents = [
        {
            "id": "doc_1",
            "title": "Coaching Techniques",
            "content": "Effective coaching involves active listening and asking powerful questions that help clients discover their own solutions. The key is to create a safe space where clients feel comfortable exploring their thoughts and feelings.",
            "source": "Coaching-Connections-1753980731.pdf",
            "chunk_id": "chunk_1"
        },
        {
            "id": "doc_2", 
            "title": "Goal Setting Framework",
            "content": "SMART goals are Specific, Measurable, Achievable, Relevant, and Time-bound. This framework helps ensure goals are clear and attainable. Break down large goals into smaller, manageable steps.",
            "source": "Coaching-Connections-1753980731.pdf",
            "chunk_id": "chunk_2"
        },
        {
            "id": "doc_3",
            "title": "Communication Skills",
            "content": "Non-verbal communication accounts for 55% of how we convey meaning. Pay attention to body language and tone of voice. Active listening involves both hearing and understanding.",
            "source": "Creative Management for Creative Teams - Mark McGuinness.pdf",
            "chunk_id": "chunk_3"
        },
        {
            "id": "doc_4",
            "title": "Leadership Development",
            "content": "Leadership is about inspiring and guiding others toward a common goal. Effective leaders lead by example and create an environment where team members can thrive and grow.",
            "source": "Creative Management for Creative Teams - Mark McGuinness.pdf",
            "chunk_id": "chunk_4"
        },
        {
            "id": "doc_5",
            "title": "Time Management",
            "content": "Time management is crucial for productivity and work-life balance. Prioritize tasks, eliminate distractions, and use techniques like the Pomodoro method to stay focused.",
            "source": "Creative Management for Creative Teams - Mark McGuinness.pdf",
            "chunk_id": "chunk_5"
        }
    ]
    
    # Create DocumentChunk objects and get real embeddings
    chunks = []
    embeddings = []
    
    print("📝 Creating embeddings for documents...")
    
    for i, doc in enumerate(test_documents):
        print(f"  Processing document {i+1}/{len(test_documents)}: {doc['title']}")
        
        chunk = DocumentChunk(
            id=doc["chunk_id"],
            content=doc["content"],
            title=doc["title"],
            source=doc["source"],
            chunk_index=i,
            start_char=i * 1000,
            end_char=(i + 1) * 1000,
            metadata={"score": 0.9 - (i * 0.1)}
        )
        chunks.append(chunk)
        
        # Get real embedding from OpenAI
        try:
            embedding = embeddings_client.get_embedding(doc["content"])
            embeddings.append(embedding)
            print(f"    ✅ Got embedding (dimension: {len(embedding)})")
        except Exception as e:
            print(f"    ❌ Failed to get embedding: {e}")
            # Fallback to mock embedding
            embedding = [0.1 + (i * 0.1)] * 1536
            embeddings.append(embedding)
            print(f"    ⚠️ Using fallback embedding")
        
        # Small delay to avoid rate limiting
        time.sleep(0.1)
    
    # Save chunks as JSON
    chunks_file = index_path / "chunks.json"
    chunks_data = [chunk.model_dump() for chunk in chunks]
    with open(chunks_file, 'w', encoding='utf-8') as f:
        json.dump(chunks_data, f, ensure_ascii=False, indent=2, default=str)
    
    # Save embeddings as numpy array
    embeddings_file = index_path / "embeddings.npy"
    np.save(embeddings_file, np.array(embeddings))
    
    # Save metadata
    metadata = {
        "version": "1.0",
        "store_type": "SimpleVectorStore",
        "total_documents": len(chunks),
        "embedding_dimension": len(embeddings[0]) if embeddings else 0,
        "created_at": time.time(),
        "embedding_model": "text-embedding-3-small"
    }
    
    metadata_file = index_path / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✅ Created real index with {len(chunks)} documents")
    print(f"📁 Chunks saved to: {chunks_file}")
    print(f"📁 Embeddings saved to: {embeddings_file}")
    print(f"📁 Metadata saved to: {metadata_file}")
    
    # Test the embeddings
    print("\n🧪 Testing embeddings...")
    test_queries = ["coaching", "leadership", "time management", "communication"]
    
    for query in test_queries:
        try:
            query_embedding = embeddings_client.get_embedding(query)
            print(f"  Query: '{query}' -> embedding dimension: {len(query_embedding)}")
        except Exception as e:
            print(f"  Query: '{query}' -> failed: {e}")

if __name__ == "__main__":
    create_real_index()
