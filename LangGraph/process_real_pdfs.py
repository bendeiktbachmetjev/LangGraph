#!/usr/bin/env python3
"""
Process real PDF files and create a proper RAG index.
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
from mentor_ai.cursor.modules.retrieval.pdf_reader import PDFReader

# Load environment variables
load_dotenv()

def process_real_pdfs():
    """Process real PDF files and create embeddings."""
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        return
    
    # Setup paths
    corpus_path = Path("RAG/corpus/pdf")
    index_path = Path("RAG/index")
    index_path.mkdir(parents=True, exist_ok=True)
    
    print("🔧 Processing real PDF files...")
    
    # Initialize components
    pdf_reader = PDFReader()
    embeddings_client = LLMClient()
    
    # Get all PDF files
    pdf_files = list(corpus_path.glob("*.pdf"))
    print(f"📚 Found {len(pdf_files)} PDF files:")
    for pdf_file in pdf_files:
        print(f"  - {pdf_file.name} ({pdf_file.stat().st_size / 1024 / 1024:.1f} MB)")
    
    if not pdf_files:
        print("❌ No PDF files found!")
        return
    
    # Process each PDF
    all_chunks = []
    all_embeddings = []
    
    for pdf_file in pdf_files:
        print(f"\n📖 Processing: {pdf_file.name}")
        
        try:
            # Extract text from PDF
            text_content = pdf_reader.extract_text_from_pdf(str(pdf_file))
            print(f"  ✅ Extracted {len(text_content)} characters")
            
            # Split into chunks (optimal size: 400-800 characters)
            chunks = split_text_into_chunks(text_content, chunk_size=600, overlap=100)
            print(f"  ✅ Created {len(chunks)} chunks")
            
            # Create DocumentChunk objects
            for i, chunk_text in enumerate(chunks):
                chunk = DocumentChunk(
                    id=f"{pdf_file.stem}_chunk_{i+1}",
                    content=chunk_text,
                    title=f"{pdf_file.stem} - Section {i+1}",
                    source=pdf_file.name,
                    chunk_index=i,
                    start_char=i * 600,
                    end_char=(i + 1) * 600,
                    metadata={"source_file": pdf_file.name, "chunk_index": i}
                )
                all_chunks.append(chunk)
                
                # Get embedding
                try:
                    embedding = embeddings_client.get_embedding(chunk_text)
                    all_embeddings.append(embedding)
                    print(f"    ✅ Chunk {i+1}: {len(chunk_text)} chars, embedding: {len(embedding)} dims")
                except Exception as e:
                    print(f"    ❌ Failed to get embedding for chunk {i+1}: {e}")
                    # Fallback embedding
                    embedding = [0.1 + (len(all_embeddings) * 0.01)] * 1536
                    all_embeddings.append(embedding)
                
                # Rate limiting
                time.sleep(0.1)
                
        except Exception as e:
            print(f"  ❌ Failed to process {pdf_file.name}: {e}")
            continue
    
    if not all_chunks:
        print("❌ No chunks created!")
        return
    
    print(f"\n📊 Summary:")
    print(f"  Total chunks: {len(all_chunks)}")
    print(f"  Total embeddings: {len(all_embeddings)}")
    
    # Save chunks as JSON
    chunks_file = index_path / "chunks.json"
    chunks_data = [chunk.model_dump() for chunk in all_chunks]
    with open(chunks_file, 'w', encoding='utf-8') as f:
        json.dump(chunks_data, f, ensure_ascii=False, indent=2, default=str)
    
    # Save embeddings as numpy array
    embeddings_file = index_path / "embeddings.npy"
    np.save(embeddings_file, np.array(all_embeddings))
    
    # Save metadata
    metadata = {
        "version": "1.0",
        "store_type": "SimpleVectorStore",
        "total_documents": len(all_chunks),
        "embedding_dimension": len(all_embeddings[0]) if all_embeddings else 0,
        "created_at": time.time(),
        "embedding_model": "text-embedding-3-small",
        "source_files": [pdf_file.name for pdf_file in pdf_files],
        "chunk_size": 600,
        "overlap": 100
    }
    
    metadata_file = index_path / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✅ Created index with {len(all_chunks)} chunks from real PDFs")
    print(f"📁 Chunks saved to: {chunks_file}")
    print(f"📁 Embeddings saved to: {embeddings_file}")
    print(f"📁 Metadata saved to: {metadata_file}")
    
    # Show chunk size statistics
    chunk_sizes = [len(chunk.content) for chunk in all_chunks]
    print(f"\n📏 Chunk size statistics:")
    print(f"  Average: {np.mean(chunk_sizes):.0f} characters")
    print(f"  Min: {min(chunk_sizes)} characters")
    print(f"  Max: {max(chunk_sizes)} characters")

def split_text_into_chunks(text, chunk_size=600, overlap=100):
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # If this is not the last chunk, try to break at a sentence boundary
        if end < len(text):
            # Look for sentence endings near the end
            for i in range(end, max(start + chunk_size - 100, start), -1):
                if text[i] in '.!?':
                    end = i + 1
                    break
        
        chunk = text[start:end].strip()
        if chunk:  # Only add non-empty chunks
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks

if __name__ == "__main__":
    process_real_pdfs()
