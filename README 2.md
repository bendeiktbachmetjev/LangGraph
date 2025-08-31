# 🎯 Mentor AI - Voice-Based Career Coaching Platform

<div align="center">

![Mentor AI Logo](https://img.shields.io/badge/Mentor-AI-blue?style=for-the-badge&logo=robot)
![Platform](https://img.shields.io/badge/Platform-iOS%20%7C%20Backend-lightgrey?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production%20Ready-green?style=for-the-badge)

**Revolutionary AI-powered career mentorship platform with personalized 12-week coaching plans**

[Features](#-main-features) • [Architecture](#-architecture) • [Quick Start](#-quick-start) • [API Reference](#-api-reference) • [Development](#-development)

</div>

---

## 🚀 Overview

Mentor AI is a cutting-edge voice-based coaching application that provides real-time feedback and personalized career development through intelligent AI agents. The platform combines advanced speech analysis, LangGraph-powered conversational flows, and comprehensive progress tracking to deliver transformative career mentorship experiences.

### Core Value Proposition

- **Personalized Career Coaching**: AI-generated 12-week plans tailored to individual career goals
- **Real-Time Voice Analysis**: Instant feedback on communication and presentation skills  
- **Intelligent Conversation Flow**: LangGraph-powered agents that adapt to user responses
- **Progress Visualization**: Comprehensive dashboard for tracking career development
- **Seamless iOS Experience**: Native SwiftUI interface with intuitive navigation

---

## ✨ Main Features

### 🎯 Goal-Based Career Coaching
- **Four Career Scenarios**: Career improvement, career change, career discovery, and exploration mode
- **Intelligent Goal Classification**: AI automatically categorizes user intentions and adapts the coaching approach
- **Personalized Pathways**: Each scenario follows a unique conversational flow optimized for specific career needs

### 🗣️ Real-Time Voice Analysis
- **OpenAI Whisper Integration**: Advanced speech-to-text transcription
- **Communication Feedback**: Instant analysis of speaking patterns and presentation skills
- **Voice Quality Assessment**: Professional communication improvement suggestions

### 📋 12-Week Personalized Plans
- **AI-Generated Roadmaps**: Comprehensive career development plans with weekly topics
- **Adaptive Content**: Plans evolve based on user progress and feedback
- **RAG-Enhanced Knowledge**: Retrieval-Augmented Generation for evidence-based coaching

### 📊 Progress Tracking
- **Visual Dashboards**: Intuitive progress visualization and milestone tracking
- **Performance Metrics**: Detailed analytics on career development progress
- **Achievement Recognition**: Celebration of milestones and accomplishments

### 💬 Weekly Coaching Sessions
- **Dedicated Chat Interfaces**: Specialized conversations for each week's topic
- **Context-Aware Responses**: AI remembers previous sessions and builds on progress
- **Flexible Scheduling**: On-demand coaching sessions that fit user schedules

---

## 🏗️ Architecture

### Backend Stack (LangGraph + FastAPI)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   iOS Frontend  │◄──►│  FastAPI Server │◄──►│  LangGraph Agent│
│   (SwiftUI)     │    │   (Python)      │    │   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   MongoDB       │    │   OpenAI API    │
                       │   (State Store) │    │   (LLM + RAG)   │
                       └─────────────────┘    └─────────────────┘
```

### LangGraph Agent Flow

The conversational agent follows a sophisticated node-based architecture:

```
collect_basic_info
       │
       ▼
classify_category ──┐
       │           │
       ▼           ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│improve_intro│ │change_intro │ │find_intro   │ │lost_intro   │
│(Career      │ │(Career      │ │(Career      │ │(Exploration │
│Improvement) │ │Change)      │ │Discovery)   │ │Mode)        │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
       │               │               │               │
       ▼               ▼               ▼               ▼
improve_skills   change_skills   find_skills     lost_skills
       │               │               │               │
       ▼               ▼               ▼               ▼
improve_obstacles change_obstacles find_obstacles     │
       │               │               │               │
       └───────────────┼───────────────┼───────────────┘
                       ▼
                retrieve_reg (RAG)
                       │
                       ▼
                generate_plan
                       │
                       ▼
                 week1_chat
```

### Four Career Scenarios

1. **Career Improvement** (`career_improve`)
   - For professionals seeking to enhance current role performance
   - Focuses on skill development and obstacle identification

2. **Career Change** (`career_change`) 
   - For individuals transitioning to new industries or roles
   - Emphasizes transferable skills and goal setting

3. **Career Discovery** (`career_find`)
   - For job seekers or career explorers
   - Helps identify passions and potential career paths

4. **Exploration Mode** (`no_goal`)
   - For users without specific career objectives
   - Facilitates self-discovery and possibility exploration

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Xcode 14+ (for iOS development)
- MongoDB instance
- OpenAI API key
- Firebase project (for authentication)

### Backend Setup

1. **Clone and Navigate**
   ```bash
   git clone <repository-url>
   cd LangGraph/LangGraph/LangGraph
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Configure your environment variables
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Server**
   ```bash
   # Kill existing processes on port 8000
   lsof -ti:8000 | xargs kill -9
   
   # Start the FastAPI server
   uvicorn mentor_ai.app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### iOS Frontend Setup

1. **Open in Xcode**
   ```bash
   cd frontend
   open MentorAI.xcodeproj
   ```

2. **Configure Firebase**
   - Add your `GoogleService-Info.plist` to the project
   - Update Firebase configuration in `AppDelegate.swift`

3. **Build and Run**
   - Select your target device/simulator
   - Press `Cmd+R` to build and run

---

## 📡 API Reference

All endpoints require an `Authorization` header with a valid Firebase ID Token.

### Session Management

#### Create Session
```http
POST /session
Authorization: Bearer <firebase_id_token>

Response: {
  "session_id": "uuid-string",
  "message": "Session created successfully"
}
```

#### Get User Session
```http
GET /user/session
Authorization: Bearer <firebase_id_token>

Response: {
  "session": {
    "session_id": "uuid-string",
    "current_node": "collect_basic_info",
    "history": [...],
    ...
  }
}
```

### Chat & Onboarding

#### Send Message
```http
POST /chat/{session_id}
Authorization: Bearer <firebase_id_token>
Content-Type: application/json

{
  "message": "I want to improve my career in software development"
}

Response: {
  "reply": "Great! I'd love to help you improve your software development career...",
  "session_id": "uuid-string"
}
```

### Data Retrieval

#### Get User Goal
```http
GET /goal/{session_id}
Authorization: Bearer <firebase_id_token>

Response: {
  "session_id": "uuid-string", 
  "goal": "software development career"
}
```

#### Get 12-Week Plan
```http
GET /topics/{session_id}
Authorization: Bearer <firebase_id_token>

Response: {
  "session_id": "uuid-string",
  "topics": {
    "week_1_topic": "Technical Skill Assessment",
    "week_2_topic": "Communication Enhancement",
    ...
    "week_12_topic": "Career Vision Planning"
  }
}
```

#### Get Full State (Debug)
```http
GET /state/{session_id}
Authorization: Bearer <firebase_id_token>

Response: {
  "session_id": "uuid-string",
  "state": {
    "user_name": "John",
    "user_age": 28,
    "goal_type": "career_improve",
    "skills": ["Python", "React"],
    "goals": ["Improve leadership", "Learn system design"],
    "plan": {...},
    "current_node": "generate_plan",
    "history": [...]
  }
}
```

---

## 🧠 LangGraph Agent Details

### Node Structure

Each node in the conversational flow follows a consistent pattern:

```python
class Node:
    def __init__(self, node_id: str, system_prompt: str, outputs: Dict[str, Any], 
                 next_node: Optional[Callable] = None, executor: Optional[Callable] = None):
        self.node_id = node_id
        self.system_prompt = system_prompt
        self.outputs = outputs  # Expected LLM outputs
        self.next_node = next_node  # Next node determination function
        self.executor = executor  # Optional non-LLM execution
```

### State Management

The agent maintains comprehensive state throughout the conversation:

```python
class SessionState(BaseModel):
    session_id: str
    user_name: Optional[str]
    user_age: Optional[int]
    goal_type: Optional[Literal["career_improve", "career_change", "career_find", "no_goal"]]
    skills: Optional[List[str]]
    interests: Optional[List[str]]
    goals: Optional[List[str]]
    plan: Optional[Dict[str, str]]  # 12-week plan
    current_node: str = "collect_basic_info"
    history: List[dict] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
```

### RAG Integration

The `retrieve_reg` node integrates Retrieval-Augmented Generation:

- **Knowledge Base**: Curated career coaching content
- **Semantic Search**: Context-aware document retrieval
- **Enhanced Responses**: Evidence-based coaching recommendations

---

## 🔧 Development

### Project Structure

```
Mentor AI/
├── LangGraph/                    # Backend implementation
│   └── LangGraph/
│       └── LangGraph/
│           └── mentor_ai/
│               ├── app/          # FastAPI application
│               │   ├── endpoints/ # API routes
│               │   ├── models.py  # Pydantic models
│               │   └── main.py   # FastAPI app
│               └── cursor/       # LangGraph implementation
│                   ├── core/     # Core graph logic
│                   ├── modules/  # Specialized modules
│                   └── postprocessing/
├── frontend/                     # iOS SwiftUI application
│   ├── Views/                   # SwiftUI views
│   ├── Components/              # Reusable components
│   ├── Models/                  # Data models
│   └── Services/                # API services
└── docs/                        # Documentation
```

### Key Components

- **GraphProcessor**: Orchestrates node transitions and LLM interactions
- **StateManager**: Handles session state persistence and retrieval
- **LLMClient**: Manages OpenAI API communication
- **MongoDBManager**: Database operations and session storage

### Testing

```bash
# Run backend tests
cd LangGraph/LangGraph/LangGraph
python -m pytest tests/

# Run specific test
python -m pytest tests/test_full_agent_plan.py -v
```

---

## 🚀 Deployment

### Railway Deployment

The application is configured for Railway deployment with:

- **Automatic scaling** based on traffic
- **Environment variable management**
- **MongoDB Atlas integration**
- **Continuous deployment** from main branch

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_openai_key
MONGODB_URI=your_mongodb_connection_string
FIREBASE_CREDENTIALS_JSON=your_firebase_json

# Optional
REG_ENABLED=true
RAG_INDEX_PATH=/app/rag_index
MAX_CONTEXT_CHARS=4000
DEBUG=false
```

---

## 📱 iOS Integration

### OnboardingManager

The iOS app uses `OnboardingManager` to handle the coaching flow:

```swift
class OnboardingManager: ObservableObject {
    @Published var phase: String = "incomplete"
    @Published var sessionId: String?
    
    var isOnboardingComplete: Bool { 
        phase == "plan_ready" 
    }
    
    func createSession() async { ... }
    func sendMessage(_ message: String) async { ... }
    func fetchPlan() async { ... }
}
```

### MyCoach Section

The "MyCoach" section is unlocked when `phase == "plan_ready"`:

```swift
if onboardingManager.isOnboardingComplete {
    // Display 12-week plan and weekly chats
    MyCoachView()
} else {
    // Show onboarding prompt
    OnboardingPromptView()
}
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow the existing code architecture and patterns
- Write comprehensive tests for new features
- Update documentation for API changes
- Ensure all tests pass before submitting PRs

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

- **Documentation**: Check the `/docs` folder for detailed guides
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Join community discussions for questions and ideas

---

<div align="center">

**Built with ❤️ using LangGraph, FastAPI, and SwiftUI**

[Back to Top](#-mentor-ai---voice-based-career-coaching-platform)

</div> 