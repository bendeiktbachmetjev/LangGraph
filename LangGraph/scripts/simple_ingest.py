#!/usr/bin/env python3
"""
Simple document ingestion script for RAG index.
"""

import sys
import os
import json
import logging
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
import openai

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# RAG Configuration
REG_ENABLED = True
EMBEDDINGS_MODEL = "text-embedding-3-small"
RETRIEVE_TOP_K = 5
MAX_CHARS_PER_CHUNK = 1000
MAX_CONTEXT_CHARS = 3000
PDF_MAX_PAGES = 100

try:
    from pdfminer.high_level import extract_text
    from pdfminer.layout import LAParams
    PDFMINER_AVAILABLE = True
except ImportError:
    PDFMINER_AVAILABLE = False
    logger.warning("pdfminer.six not available. PDF processing will be disabled.")


class SimpleDocumentChunk:
    """Simple document chunk representation."""
    
    def __init__(self, id: str, content: str, title: str, source: str, chunk_index: int, start_char: int, end_char: int, metadata: Dict[str, Any]):
        self.id = id
        self.content = content
        self.title = title
        self.source = source
        self.chunk_index = chunk_index
        self.start_char = start_char
        self.end_char = end_char
        self.metadata = metadata
    
    def dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "title": self.title,
            "source": self.source,
            "chunk_index": self.chunk_index,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "metadata": self.metadata
        }


class SimpleVectorStore:
    """Simple vector store using numpy arrays and cosine similarity."""
    
    def __init__(self):
        self.chunks = []
        self.embeddings = []
        
    def add_documents(self, chunks: List[SimpleDocumentChunk], embeddings: List[List[float]]) -> None:
        """Add document chunks with their embeddings to the store."""
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
            
        # Add new chunks and embeddings
        self.chunks.extend(chunks)
        self.embeddings.extend(embeddings)
        
        logger.info(f"Added {len(chunks)} documents to vector store. Total: {len(self.chunks)}")
    
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
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, ensure_ascii=False, indent=2)
        
        # Save embeddings as JSON (simplified)
        embeddings_file = path / "embeddings.json"
        with open(embeddings_file, 'w') as f:
            json.dump(self.embeddings, f)
        
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
    
    def clear(self) -> None:
        """Clear all data from the store."""
        self.chunks.clear()
        self.embeddings.clear()
        logger.info("Cleared vector store")


class PDFReader:
    """Extracts text from PDF files using pdfminer.six."""
    
    def __init__(self, max_pages: int = 100):
        self.max_pages = max_pages
        
    def extract_text_from_pdf(self, pdf_path: str) -> Optional[str]:
        """Extract text from a PDF file."""
        if not PDFMINER_AVAILABLE:
            logger.error("pdfminer.six not available. Cannot extract text from PDF.")
            return None
            
        try:
            pdf_path = Path(pdf_path)
            if not pdf_path.exists():
                logger.error(f"PDF file not found: {pdf_path}")
                return None
                
            logger.info(f"Extracting text from PDF: {pdf_path}")
            
            # Configure layout analysis parameters for better text extraction
            laparams = LAParams(
                line_margin=0.5,
                word_margin=0.1,
                char_margin=2.0,
                boxes_flow=0.5,
                detect_vertical=True
            )
            
            # Extract text
            text = extract_text(
                str(pdf_path),
                laparams=laparams,
                maxpages=self.max_pages
            )
            
            if not text or not text.strip():
                logger.warning(f"No text extracted from PDF: {pdf_path}")
                return None
                
            # Clean up the extracted text
            cleaned_text = self._clean_text(text)
            
            logger.info(f"Successfully extracted {len(cleaned_text)} characters from {pdf_path}")
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return ""
            
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove excessive spaces
            line = ' '.join(line.split())
            
            # Skip empty lines
            if line.strip():
                cleaned_lines.append(line)
        
        # Join lines with proper spacing
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Remove common PDF artifacts
        cleaned_text = cleaned_text.replace('\x00', '')  # Null bytes
        cleaned_text = cleaned_text.replace('\r', '\n')  # Normalize line endings
        
        return cleaned_text


class DocumentIngester:
    """Handles document ingestion and indexing."""
    
    def __init__(self):
        self.vector_store = SimpleVectorStore()
        self.pdf_reader = PDFReader(max_pages=PDF_MAX_PAGES)
        
    def ingest_corpus(self, corpus_path: str, index_path: str) -> None:
        """Ingest all documents from corpus and create vector index."""
        logger.info(f"Starting corpus ingestion from {corpus_path}")
        start_time = time.time()
        
        # Clear existing index
        self.vector_store.clear()
        
        # Process PDF files
        pdf_path = Path(corpus_path) / "pdf"
        if pdf_path.exists():
            self._process_pdf_files(pdf_path)
        
        # Save the index
        self.vector_store.save(index_path)
        
        total_time = time.time() - start_time
        stats = self.vector_store.get_stats()
        
        logger.info(f"Ingestion completed in {total_time:.2f}s. Indexed {stats['total_documents']} documents.")
    
    def _process_pdf_files(self, pdf_dir: Path) -> None:
        """Process all PDF files in the directory."""
        pdf_files = list(pdf_dir.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            try:
                self._process_pdf_file(pdf_file)
            except Exception as e:
                logger.error(f"Error processing PDF {pdf_file}: {e}")
    
    def _process_pdf_file(self, pdf_file: Path) -> None:
        """Process a single PDF file."""
        logger.info(f"Processing PDF: {pdf_file.name}")
        
        # Extract text
        text = self.pdf_reader.extract_text_from_pdf(str(pdf_file))
        if not text:
            logger.warning(f"No text extracted from {pdf_file.name}")
            return
        
        # Get metadata
        metadata = self._get_document_metadata(pdf_file)
        
        # Create chunks
        chunks = self._create_chunks(text, pdf_file.name, str(pdf_file), metadata)
        
        # Get embeddings
        embeddings = self._get_embeddings([chunk.content for chunk in chunks])
        
        # Add to vector store
        self.vector_store.add_documents(chunks, embeddings)
        
        logger.info(f"Processed {pdf_file.name}: {len(chunks)} chunks")
    
    def _get_document_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Get metadata for a document."""
        # Return basic metadata
        return {
            "title": file_path.stem,
            "source": str(file_path),
            "file_type": file_path.suffix,
            "filename": file_path.name
        }
    
    def _create_chunks(self, text: str, title: str, source: str, metadata: Dict[str, Any]) -> List[SimpleDocumentChunk]:
        """Create document chunks from text."""
        chunks = []
        
        # Split text into sentences
        sentences = self._split_into_sentences(text)
        
        # Create chunks with overlap
        chunk_size = MAX_CHARS_PER_CHUNK
        overlap = chunk_size // 4  # 25% overlap
        
        current_chunk = ""
        start_char = 0
        
        for i, sentence in enumerate(sentences):
            # Check if adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                # Create chunk
                chunk = SimpleDocumentChunk(
                    id=f"{source}_{len(chunks)}",
                    content=current_chunk.strip(),
                    title=title,
                    source=source,
                    chunk_index=len(chunks),
                    start_char=start_char,
                    end_char=start_char + len(current_chunk),
                    metadata=metadata
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_start = max(0, len(current_chunk) - overlap)
                current_chunk = current_chunk[overlap_start:] + " " + sentence
                start_char = start_char + overlap_start
            else:
                current_chunk += " " + sentence
        
        # Add final chunk
        if current_chunk.strip():
            chunk = SimpleDocumentChunk(
                id=f"{source}_{len(chunks)}",
                content=current_chunk.strip(),
                title=title,
                source=source,
                chunk_index=len(chunks),
                start_char=start_char,
                end_char=start_char + len(current_chunk),
                metadata=metadata
            )
            chunks.append(chunk)
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        import re
        
        # Split on sentence endings
        sentences = re.split(r'[.!?]+', text)
        
        # Clean up sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:  # Minimum sentence length
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for a list of texts."""
        embeddings = []
        
        for text in texts:
            try:
                response = openai.Embedding.create(
                    model=EMBEDDINGS_MODEL,
                    input=text
                )
                embeddings.append(response['data'][0]['embedding'])
            except Exception as e:
                logger.error(f"Error getting embedding: {e}")
                # Return zero vector as fallback
                embeddings.append([0.0] * 1536)
        
        return embeddings


def main():
    """Main function for the ingest script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ingest documents into RAG index")
    parser.add_argument(
        "--corpus-path",
        default="LangGraph/RAG/corpus",
        help="Path to corpus directory"
    )
    parser.add_argument(
        "--index-path", 
        default="LangGraph/RAG/index",
        help="Path to save index"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-indexing even if index exists"
    )
    
    args = parser.parse_args()
    
    # Validate paths
    corpus_path = Path(args.corpus_path)
    index_path = Path(args.index_path)
    
    if not corpus_path.exists():
        logger.error(f"Corpus path does not exist: {corpus_path}")
        sys.exit(1)
    
    # Check if index already exists
    if index_path.exists() and not args.force:
        logger.warning(f"Index already exists at {index_path}")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            logger.info("Aborting ingestion.")
            sys.exit(0)
    
    try:
        # Initialize ingester
        ingester = DocumentIngester()
        
        # Run ingestion
        logger.info(f"Starting ingestion from {corpus_path} to {index_path}")
        ingester.ingest_corpus(str(corpus_path), str(index_path))
        
        logger.info("Ingestion completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
