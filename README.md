# Mentor AI - Personal Goal Planning Assistant

An intelligent conversational AI agent that helps users create personalized 12-week plans for achieving their goals.

## Features

- **Goal Classification**: Automatically categorizes user goals (career, relationships, health, etc.)
- **Personalized Planning**: Generates customized 12-week action plans
- **Conversational Interface**: Natural language interaction with users
- **Session Management**: Persistent conversation state
- **MongoDB Integration**: Reliable data storage

## Tech Stack

- **Backend**: FastAPI + Python
- **AI**: OpenAI GPT-4 + LangChain
- **Database**: MongoDB
- **Deployment**: Render

## API Endpoints

- `POST /session` - Create new session
- `POST /chat/{session_id}` - Send message to AI
- `GET /goal/{session_id}` - Get user's goal
- `GET /topics/{session_id}` - Get generated plan topics

## Environment Variables

- `OPENAI_API_KEY` - Your OpenAI API key
- `MONGODB_URI` - MongoDB connection string
- `PORT` - Server port (set by Render)

## Local Development

1. Clone the repository
2. Install dependencies: `pip install -r mentor_ai/requirements.txt`
3. Set environment variables
4. Run: `uvicorn mentor_ai.app.main:app --reload`

## Deployment on Render

1. Connect your GitHub repository to Render
2. Set environment variables in Render dashboard:
   - `OPENAI_API_KEY`
   - `MONGODB_URI`
3. Deploy automatically using `render.yaml`

## Project Structure

```
mentor_ai/
├── app/                 # FastAPI application
│   ├── endpoints/      # API routes
│   ├── storage/        # Database layer
│   └── main.py         # Application entry point
├── cursor/             # Core AI logic
│   ├── core/          # Graph processing, LLM client
│   └── modules/       # AI modules
└── tests/             # Test suite
``` 