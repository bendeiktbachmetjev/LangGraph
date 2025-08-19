from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from dotenv import load_dotenv
from mentor_ai.app.storage.mongodb import mongodb_manager
from mentor_ai.app.endpoints import session_router, chat_router
import firebase_admin
from firebase_admin import credentials
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Firebase Admin SDK from JSON in env variable
firebase_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
if firebase_json and not firebase_admin._apps:
    cred_dict = json.loads(firebase_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

# Create FastAPI app
app = FastAPI(
    title="Mentor AI",
    description="A conversational AI agent that helps users create personalized goals and topics",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session_router)
app.include_router(chat_router)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Mentor AI API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "mentor_ai"}

@app.on_event("startup")
async def startup_event():
    """Connect to MongoDB on startup"""
    try:
        await mongodb_manager.connect()
        logger.info("✅ Application started successfully")
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Disconnect from MongoDB on shutdown"""
    await mongodb_manager.disconnect()
    logger.info("Application shutdown complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "mentor_ai.app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "True").lower() == "true"
    ) 