"""
PDF text extraction module using pdfminer.six.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from pdfminer.high_level import extract_text
    from pdfminer.layout import LAParams
    PDFMINER_AVAILABLE = True
except ImportError:
    PDFMINER_AVAILABLE = False
    logging.warning("pdfminer.six not available. PDF processing will be disabled.")

logger = logging.getLogger(__name__)


class PDFReader:
    """Extracts text from PDF files using pdfminer.six."""
    
    def __init__(self, max_pages: int = 100):
        self.max_pages = max_pages
        
    def extract_text_from_pdf(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text or None if extraction fails
        """
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
        """
        Clean and normalize extracted text.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
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
        
        # Remove page numbers and headers/footers (simple heuristics)
        lines = cleaned_text.split('\n')
        filtered_lines = []
        
        for line in lines:
            # Skip lines that look like page numbers
            if line.strip().isdigit() and len(line.strip()) <= 3:
                continue
                
            # Skip very short lines that might be headers/footers
            if len(line.strip()) < 5 and line.strip().isupper():
                continue
                
            filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def get_document_info(self, pdf_path: str) -> Dict[str, Any]:
        """
        Get basic information about a PDF document.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with document information
        """
        try:
            pdf_path = Path(pdf_path)
            stat = pdf_path.stat()
            
            return {
                "filename": pdf_path.name,
                "size_bytes": stat.st_size,
                "modified_time": stat.st_mtime,
                "exists": True
            }
        except Exception as e:
            logger.error(f"Error getting document info for {pdf_path}: {e}")
            return {
                "filename": str(pdf_path),
                "exists": False,
                "error": str(e)
            }
