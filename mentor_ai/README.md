# Mentor AI

A conversational AI agent that helps users create personalized goals and topics through natural conversation.

## Features

- Natural conversation flow with LLM agent
- Personalized goal and topic generation
- MongoDB storage for session management
- RESTful API endpoints

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with the following content:

```
OPENAI_API_KEY=your_openai_api_key_here
MONGODB_URI=mongodb://localhost:27017/mentor_ai
DEBUG=True
LOG_LEVEL=INFO
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

- `POST /session` - Start onboarding session
- `POST /chat/{session_id}` - Handle user messages
- `POST /plan/{session_id}` - Generate plan after onboarding
- `GET /status/{session_id}` - Get session status

## Project Structure

```
mentor_ai/
├── cursor/           # LangGraph cursor modules
│   ├── core/         # Core functionality
│   ├── modules/      # Conversation modules
│   └── postprocessing/ # Plan generation
├── app/              # FastAPI application
│   ├── graphs/       # LangGraph definitions
│   ├── endpoints/    # API endpoints
│   └── storage/      # Database operations
└── tests/            # Test files
``` 