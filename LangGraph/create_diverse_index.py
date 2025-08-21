#!/usr/bin/env python3
"""
Create a diverse RAG index with many different documents for proper testing.
"""

import os
import sys
import json
import time
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from mentor_ai.cursor.modules.retrieval.schemas import DocumentChunk
from mentor_ai.cursor.core.llm_client import LLMClient

# Load environment variables
load_dotenv()

def create_diverse_index():
    """Create a diverse RAG index with many different documents."""
    
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        return
    
    # Setup paths
    index_path = Path("RAG/index")
    index_path.mkdir(parents=True, exist_ok=True)
    
    print("🔧 Creating diverse RAG index with many documents...")
    
    # Initialize OpenAI embeddings client
    embeddings_client = LLMClient()
    
    # Create diverse test documents
    diverse_documents = [
        # Coaching & Mentoring
        {
            "title": "Active Listening Techniques",
            "content": "Active listening involves fully concentrating on what is being said rather than just passively hearing the message. Use techniques like paraphrasing, asking clarifying questions, and providing nonverbal feedback.",
            "source": "Coaching-Connections-1753980731.pdf",
            "category": "coaching"
        },
        {
            "title": "Powerful Questioning Methods",
            "content": "Powerful questions are open-ended and thought-provoking. They help clients explore their thoughts and discover their own solutions. Examples include 'What would success look like?' and 'What's stopping you?'",
            "source": "Coaching-Connections-1753980731.pdf",
            "category": "coaching"
        },
        {
            "title": "Goal Setting Strategies",
            "content": "SMART goals are Specific, Measurable, Achievable, Relevant, and Time-bound. Break down large goals into smaller, manageable steps and track progress regularly.",
            "source": "Coaching-Connections-1753980731.pdf",
            "category": "goal-setting"
        },
        
        # Leadership
        {
            "title": "Transformational Leadership",
            "content": "Transformational leaders inspire and motivate their team members to exceed expectations. They create a vision, communicate it effectively, and lead by example.",
            "source": "Creative Management for Creative Teams - Mark McGuinness.pdf",
            "category": "leadership"
        },
        {
            "title": "Team Building Activities",
            "content": "Effective team building activities include trust exercises, problem-solving challenges, and collaborative projects. Focus on building communication and trust among team members.",
            "source": "Creative Management for Creative Teams - Mark McGuinness.pdf",
            "category": "leadership"
        },
        {
            "title": "Conflict Resolution Skills",
            "content": "Conflict resolution involves identifying the root cause of disagreements, facilitating open communication, and finding mutually acceptable solutions.",
            "source": "Creative Management for Creative Teams - Mark McGuinness.pdf",
            "category": "leadership"
        },
        
        # Communication
        {
            "title": "Nonverbal Communication",
            "content": "Nonverbal communication includes body language, facial expressions, gestures, and tone of voice. It accounts for 55% of how we convey meaning in conversations.",
            "source": "Creative Management for Creative Teams - Mark McGuinness.pdf",
            "category": "communication"
        },
        {
            "title": "Public Speaking Tips",
            "content": "Effective public speaking involves preparation, practice, and confidence. Use storytelling, maintain eye contact, and speak clearly with appropriate pacing.",
            "source": "Creative Management for Creative Teams - Mark McGuinness.pdf",
            "category": "communication"
        },
        {
            "title": "Written Communication",
            "content": "Clear written communication uses simple language, proper structure, and active voice. Avoid jargon and ensure your message is easily understood by the intended audience.",
            "source": "Creative Management for Creative Teams - Mark McGuinness.pdf",
            "category": "communication"
        },
        
        # Time Management
        {
            "title": "Pomodoro Technique",
            "content": "The Pomodoro Technique involves working for 25 minutes followed by a 5-minute break. This helps maintain focus and prevent burnout during long work sessions.",
            "source": "Creative Management for Creative Teams - Mark McGuinness.pdf",
            "category": "time-management"
        },
        {
            "title": "Priority Matrix",
            "content": "Use a priority matrix to categorize tasks by urgency and importance. Focus on important and urgent tasks first, then important but not urgent tasks.",
            "source": "Creative Management for Creative Teams - Mark McGuinness.pdf",
            "category": "time-management"
        },
        {
            "title": "Delegation Strategies",
            "content": "Effective delegation involves identifying the right person for the task, providing clear instructions, and following up on progress without micromanaging.",
            "source": "Creative Management for Creative Teams - Mark McGuinness.pdf",
            "category": "time-management"
        },
        
        # Creativity & Innovation
        {
            "title": "Brainstorming Techniques",
            "content": "Effective brainstorming involves generating many ideas without judgment, building on others' ideas, and encouraging creative thinking through various techniques.",
            "source": "Creative Management for Creative Teams - Mark McGuinness.pdf",
            "category": "creativity"
        },
        {
            "title": "Design Thinking Process",
            "content": "Design thinking involves empathizing with users, defining problems, ideating solutions, prototyping, and testing to create innovative solutions.",
            "source": "Creative Management for Creative Teams - Mark McGuinness.pdf",
            "category": "creativity"
        },
        {
            "title": "Innovation Management",
            "content": "Innovation management involves creating a culture that encourages new ideas, providing resources for experimentation, and implementing successful innovations.",
            "source": "Creative Management for Creative Teams - Mark McGuinness.pdf",
            "category": "creativity"
        },
        
        # Productivity
        {
            "title": "Work-Life Balance",
            "content": "Maintaining work-life balance involves setting boundaries, prioritizing personal time, and ensuring that work doesn't consume all aspects of life.",
            "source": "Creative Management for Creative Teams - Mark McGuinness.pdf",
            "category": "productivity"
        },
        {
            "title": "Stress Management",
            "content": "Effective stress management includes regular exercise, mindfulness practices, time management, and seeking support when needed.",
            "source": "Creative Management for Creative Teams - Mark McGuinness.pdf",
            "category": "productivity"
        },
        {
            "title": "Energy Management",
            "content": "Energy management involves understanding your natural rhythms, scheduling important tasks during peak energy times, and taking breaks to recharge.",
            "source": "Creative Management for Creative Teams - Mark McGuinness.pdf",
            "category": "productivity"
        },
        
        # Project Management
        {
            "title": "Agile Methodology",
            "content": "Agile methodology involves iterative development, regular feedback, and adapting to change. It emphasizes collaboration, customer satisfaction, and working software.",
            "source": "Creative Management for Creative Teams - Mark McGuinness.pdf",
            "category": "project-management"
        },
        {
            "title": "Risk Management",
            "content": "Risk management involves identifying potential problems, assessing their impact, and developing strategies to mitigate or avoid them.",
            "source": "Creative Management for Creative Teams - Mark McGuinness.pdf",
            "category": "project-management"
        },
        {
            "title": "Stakeholder Communication",
            "content": "Effective stakeholder communication involves understanding their needs, providing regular updates, and managing expectations throughout the project.",
            "source": "Creative Management for Creative Teams - Mark McGuinness.pdf",
            "category": "project-management"
        }
    ]
    
    # Create DocumentChunk objects and get real embeddings
    chunks = []
    embeddings = []
    
    print(f"📝 Creating embeddings for {len(diverse_documents)} documents...")
    
    for i, doc in enumerate(diverse_documents):
        print(f"  Processing document {i+1}/{len(diverse_documents)}: {doc['title']}")
        
        chunk = DocumentChunk(
            id=f"chunk_{i+1}",
            content=doc["content"],
            title=doc["title"],
            source=doc["source"],
            chunk_index=i,
            start_char=i * 1000,
            end_char=(i + 1) * 1000,
            metadata={"category": doc["category"], "score": 0.9 - (i * 0.01)}
        )
        chunks.append(chunk)
        
        # Get real embedding from OpenAI
        try:
            embedding = embeddings_client.get_embedding(doc["content"])
            embeddings.append(embedding)
            print(f"    ✅ Got embedding (dimension: {len(embedding)})")
        except Exception as e:
            print(f"    ❌ Failed to get embedding: {e}")
            # Fallback to mock embedding
            embedding = [0.1 + (i * 0.01)] * 1536
            embeddings.append(embedding)
            print(f"    ⚠️ Using fallback embedding")
        
        # Small delay to avoid rate limiting
        time.sleep(0.1)
    
    # Save chunks as JSON
    chunks_file = index_path / "chunks.json"
    chunks_data = [chunk.model_dump() for chunk in chunks]
    with open(chunks_file, 'w', encoding='utf-8') as f:
        json.dump(chunks_data, f, ensure_ascii=False, indent=2, default=str)
    
    # Save embeddings as numpy array
    embeddings_file = index_path / "embeddings.npy"
    np.save(embeddings_file, np.array(embeddings))
    
    # Save metadata
    metadata = {
        "version": "1.0",
        "store_type": "SimpleVectorStore",
        "total_documents": len(chunks),
        "embedding_dimension": len(embeddings[0]) if embeddings else 0,
        "created_at": time.time(),
        "embedding_model": "text-embedding-3-small",
        "categories": list(set([doc["category"] for doc in diverse_documents]))
    }
    
    metadata_file = index_path / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n✅ Created diverse index with {len(chunks)} documents")
    print(f"📁 Categories: {metadata['categories']}")
    print(f"📁 Chunks saved to: {chunks_file}")
    print(f"📁 Embeddings saved to: {embeddings_file}")
    print(f"📁 Metadata saved to: {metadata_file}")
    
    # Test the embeddings with diverse queries
    print("\n🧪 Testing diverse queries...")
    test_queries = [
        "coaching", "leadership", "communication", "time management", 
        "creativity", "productivity", "project management", "stress"
    ]
    
    for query in test_queries:
        try:
            query_embedding = embeddings_client.get_embedding(query)
            print(f"  Query: '{query}' -> embedding dimension: {len(query_embedding)}")
        except Exception as e:
            print(f"  Query: '{query}' -> failed: {e}")

if __name__ == "__main__":
    create_diverse_index()
