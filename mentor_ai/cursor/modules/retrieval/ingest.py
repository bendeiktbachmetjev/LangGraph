"""
Document ingestion and indexing for RAG system.
"""

import os
import json
import logging
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
import openai

from .pdf_reader import PDFReader
from .vector_store import VectorStore
from .simple_store import SimpleVectorStore
from .schemas import DocumentChunk
# from ...app.config import settings  # Will import directly in functions

logger = logging.getLogger(__name__)


class DocumentIngester:
    """Handles document ingestion and indexing."""
    
    def __init__(self, vector_store: Optional[VectorStore] = None):
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        from app.config import settings
        self.vector_store = vector_store or SimpleVectorStore()
        self.pdf_reader = PDFReader(max_pages=settings.PDF_MAX_PAGES)
        
    def ingest_corpus(self, corpus_path: str, index_path: str) -> None:
        """
        Ingest all documents from corpus and create vector index.
        
        Args:
            corpus_path: Path to corpus directory
            index_path: Path to save the index
        """
        logger.info(f"Starting corpus ingestion from {corpus_path}")
        start_time = time.time()
        
        # Clear existing index
        self.vector_store.clear()
        
        # Process PDF files
        pdf_path = Path(corpus_path) / "pdf"
        if pdf_path.exists():
            self._process_pdf_files(pdf_path)
        
        # Process text files
        txt_path = Path(corpus_path) / "txt"
        if txt_path.exists():
            self._process_text_files(txt_path)
        
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
    
    def _process_text_files(self, txt_dir: Path) -> None:
        """Process all text files in the directory."""
        txt_files = list(txt_dir.glob("*.txt")) + list(txt_dir.glob("*.md"))
        logger.info(f"Found {len(txt_files)} text files to process")
        
        for txt_file in txt_files:
            try:
                self._process_text_file(txt_file)
            except Exception as e:
                logger.error(f"Error processing text file {txt_file}: {e}")
    
    def _process_text_file(self, txt_file: Path) -> None:
        """Process a single text file."""
        logger.info(f"Processing text file: {txt_file.name}")
        
        # Read text
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            logger.error(f"Error reading text file {txt_file}: {e}")
            return
        
        if not text.strip():
            logger.warning(f"Empty text file: {txt_file.name}")
            return
        
        # Get metadata
        metadata = self._get_document_metadata(txt_file)
        
        # Create chunks
        chunks = self._create_chunks(text, txt_file.name, str(txt_file), metadata)
        
        # Get embeddings
        embeddings = self._get_embeddings([chunk.content for chunk in chunks])
        
        # Add to vector store
        self.vector_store.add_documents(chunks, embeddings)
        
        logger.info(f"Processed {txt_file.name}: {len(chunks)} chunks")
    
    def _get_document_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Get metadata for a document."""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        from app.config import settings
        # Try to load metadata from meta directory
        meta_file = Path(settings.RAG_CORPUS_PATH) / "meta" / f"{file_path.stem}.json"
        
        if meta_file.exists():
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading metadata for {file_path.name}: {e}")
        
        # Return basic metadata
        return {
            "title": file_path.stem,
            "source": str(file_path),
            "file_type": file_path.suffix,
            "filename": file_path.name
        }
    
    def _create_chunks(self, text: str, title: str, source: str, metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """Create document chunks from text."""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        from app.config import settings
        chunks = []
        
        # Split text into sentences
        sentences = self._split_into_sentences(text)
        
        # Create chunks with overlap
        chunk_size = settings.MAX_CHARS_PER_CHUNK
        overlap = chunk_size // 4  # 25% overlap
        
        current_chunk = ""
        start_char = 0
        
        for i, sentence in enumerate(sentences):
            # Check if adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                # Create chunk
                chunk = DocumentChunk(
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
            chunk = DocumentChunk(
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
        # Simple sentence splitting
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
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
        from app.config import settings
        embeddings = []
        
        for text in texts:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                response = client.embeddings.create(
                    model=settings.EMBEDDINGS_MODEL,
                    input=text
                )
                embeddings.append(response.data[0].embedding)
            except Exception as e:
                logger.error(f"Error getting embedding: {e}")
                # Return zero vector as fallback
                embeddings.append([0.0] * 1536)
        
        return embeddings
