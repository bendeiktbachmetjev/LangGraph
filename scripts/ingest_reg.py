#!/usr/bin/env python3
"""
CLI script for ingesting documents into RAG index.
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import settings locally to avoid import issues
import os
from dotenv import load_dotenv
load_dotenv()

class LocalSettings:
    RAG_CORPUS_PATH = os.getenv("RAG_CORPUS_PATH", "LangGraph/RAG/corpus")
    RAG_INDEX_PATH = os.getenv("RAG_INDEX_PATH", "LangGraph/RAG/index")

settings = LocalSettings()

from mentor_ai.cursor.modules.retrieval.ingest import DocumentIngester

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main function for the ingest script."""
    parser = argparse.ArgumentParser(description="Ingest documents into RAG index")
    parser.add_argument(
        "--corpus-path",
        default=settings.RAG_CORPUS_PATH,
        help=f"Path to corpus directory (default: {settings.RAG_CORPUS_PATH})"
    )
    parser.add_argument(
        "--index-path", 
        default=settings.RAG_INDEX_PATH,
        help=f"Path to save index (default: {settings.RAG_INDEX_PATH})"
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
