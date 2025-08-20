#!/usr/bin/env python3
"""
Simple script to create RAG index from PDF documents.
"""

import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def create_simple_index():
    """Create a simple index for testing."""
    
    # Paths
    corpus_path = Path("RAG/corpus/pdf")
    index_path = Path("RAG/index")
    
    # Create index directory if it doesn't exist
    index_path.mkdir(parents=True, exist_ok=True)
    
    # Check if PDF files exist
    pdf_files = list(corpus_path.glob("*.pdf"))
    if not pdf_files:
        print("❌ No PDF files found in RAG/corpus/pdf/")
        return
    
    print(f"📚 Found {len(pdf_files)} PDF files")
    
    # Create simple index with mock data for testing
    index_data = {
        "documents": [],
        "embeddings": {},
        "metadata": {
            "created_at": time.time(),
            "total_documents": len(pdf_files),
            "version": "1.0"
        }
    }
    
    # Add mock documents for testing
    mock_documents = [
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
    
    index_data["documents"] = mock_documents
    
    # Create DocumentChunk objects
    from mentor_ai.cursor.modules.retrieval.schemas import DocumentChunk
    
    chunks = []
    embeddings = []
    
    for i, doc in enumerate(mock_documents):
        chunk = DocumentChunk(
            id=doc["chunk_id"],
            content=doc["content"],
            title=doc["title"],
            source=doc["source"],
            chunk_index=i,
            start_char=i * 1000,
            end_char=(i + 1) * 1000,
            metadata={"score": 0.9 - (i * 0.1)}  # Decreasing scores
        )
        chunks.append(chunk)
        
        # Create mock embedding
        embedding = [0.1 + (i * 0.1)] * 1536  # Different embeddings for each chunk
        embeddings.append(embedding)
    
    # Save chunks as JSON (for SimpleVectorStore)
    chunks_file = index_path / "chunks.json"
    chunks_data = [chunk.model_dump() for chunk in chunks]
    with open(chunks_file, 'w', encoding='utf-8') as f:
        json.dump(chunks_data, f, ensure_ascii=False, indent=2, default=str)
    
    # Save embeddings as numpy array
    import numpy as np
    embeddings_file = index_path / "embeddings.npy"
    np.save(embeddings_file, np.array(embeddings))
    
    # Save metadata
    metadata = {
        "version": "1.0",
        "store_type": "SimpleVectorStore",
        "total_documents": len(chunks),
        "embedding_dimension": 1536
    }
    
    metadata_file = index_path / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✅ Created index with {len(chunks)} documents")
    print(f"📁 Chunks saved to: {chunks_file}")
    print(f"📁 Embeddings saved to: {embeddings_file}")
    print(f"📁 Metadata saved to: {metadata_file}")

if __name__ == "__main__":
    create_simple_index()
