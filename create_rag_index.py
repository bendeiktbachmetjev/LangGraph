#!/usr/bin/env python3
"""
Script to create RAG index from corpus documents.
"""

import os
import sys
import logging
from pathlib import Path

# Add the mentor_ai directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "mentor_ai"))

# Set environment variables for RAG
os.environ["REG_ENABLED"] = "true"
os.environ["EMBEDDINGS_PROVIDER"] = "openai"
os.environ["EMBEDDINGS_MODEL"] = "text-embedding-3-small"

try:
    from mentor_ai.cursor.modules.retrieval.ingest import DocumentIngester
    from mentor_ai.app.config import settings
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you have installed all dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Create RAG index from corpus documents."""
    logger.info("🚀 Starting RAG index creation...")
    
    # Get paths from settings
    corpus_path = settings.RAG_CORPUS_PATH
    index_path = settings.RAG_INDEX_PATH
    
    logger.info(f"📁 Corpus path: {corpus_path}")
    logger.info(f"📁 Index path: {index_path}")
    
    # Check if corpus exists
    if not os.path.exists(corpus_path):
        logger.error(f"❌ Corpus path does not exist: {corpus_path}")
        return False
    
    # Create index directory if it doesn't exist
    os.makedirs(index_path, exist_ok=True)
    
    try:
        # Initialize ingester
        ingester = DocumentIngester()
        
        # Ingest corpus
        ingester.ingest_corpus(corpus_path, index_path)
        
        logger.info("✅ RAG index created successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create RAG index: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
