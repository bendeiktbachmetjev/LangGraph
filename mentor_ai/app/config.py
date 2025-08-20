import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    """Application settings"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # MongoDB Configuration
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/mentor_ai")
    MONGODB_DATABASE: str = "mentor_ai"
    
    # Application Settings
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    
    # LLM Configuration
    LLM_MODEL: str = "gpt-4"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2000
    
    # RAG Configuration
    REG_ENABLED: bool = os.getenv("REG_ENABLED", "False").lower() == "true"
    EMBEDDINGS_PROVIDER: str = os.getenv("EMBEDDINGS_PROVIDER", "openai")
    EMBEDDINGS_MODEL: str = os.getenv("EMBEDDINGS_MODEL", "text-embedding-3-small")
    RAG_INDEX_PATH: str = os.getenv("RAG_INDEX_PATH", "RAG/index")
    RAG_CORPUS_PATH: str = os.getenv("RAG_CORPUS_PATH", "RAG/corpus")
    
    # RAG Limits
    RETRIEVE_TOP_K: int = int(os.getenv("RETRIEVE_TOP_K", "5"))
    MAX_CHARS_PER_CHUNK: int = int(os.getenv("MAX_CHARS_PER_CHUNK", "1000"))
    MAX_CONTEXT_CHARS: int = int(os.getenv("MAX_CONTEXT_CHARS", "3000"))
    
    # PDF Processing
    PDF_MAX_PAGES: int = int(os.getenv("PDF_MAX_PAGES", "100"))
    PDF_EXTRACTOR: str = os.getenv("PDF_EXTRACTOR", "pdfminer")
    
    @classmethod
    def validate(cls):
        """Validate required settings"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        if not cls.MONGODB_URI:
            raise ValueError("MONGODB_URI is required")
        
        # Validate RAG settings if enabled
        if cls.REG_ENABLED:
            if cls.EMBEDDINGS_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is required for OpenAI embeddings")

# Create settings instance
settings = Settings() 