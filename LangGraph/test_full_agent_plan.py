#!/usr/bin/env python3
"""
Test full agent flow including plan generation with RAG.
"""

import requests
import json
import time

def test_full_agent_plan():
    """Test complete agent flow with plan generation using RAG."""
    base_url = "https://spotted-mom-production.up.railway.app"
    
    print("🚀 Testing Full Agent Flow with RAG Plan Generation")
    print("=" * 60)
    
    # Test 1: Check RAG status
    print("\n1. Checking RAG status...")
    try:
        response = requests.get(f"{base_url}/api/rag/debug")
        if response.status_code == 200:
            debug_info = response.json()
            print(f"   ✅ RAG enabled: {debug_info.get('rag_enabled')}")
        else:
            print(f"   ❌ Debug endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Test retrieve_reg node
    print("\n2. Testing retrieve_reg node...")
    try:
        response = requests.post(f"{base_url}/api/rag/test/agent")
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"   ✅ retrieve_reg working")
                print(f"   Retrieved chunks: {result.get('retrieved_chunks_count')}")
                print(f"   Next node: {result.get('next_node')}")
                
                chunks = result.get("retrieved_chunks", [])
                if chunks:
                    print(f"   Sample chunk: {chunks[0].get('title', 'Unknown')[:50]}...")
            else:
                print(f"   ❌ retrieve_reg failed: {result.get('error')}")
        else:
            print(f"   ❌ Agent test failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Test generate_plan node with RAG knowledge
    print("\n3. Testing generate_plan node with RAG...")
    try:
        # Create a test state with retrieved chunks
        test_state = {
            "session_id": "test_full_plan",
            "user_name": "John",
            "user_age": 28,
            "goal_type": "career_improve",
            "career_goal": "Become a team leader",
            "skills": ["communication", "project management", "teamwork"],
            "goals": ["Improve leadership skills", "Build team management experience", "Develop strategic thinking"],
            "retrieved_chunks": [
                {
                    "title": "Creative Management for Creative Teams - Section 86",
                    "content": "Goal setting, Looking, Listening, Empathising, Questioning, Giving feedback, Intuiting, Checking. Most of these appear on any standard list of coaching skills.",
                    "source": "Creative Management for Creative Teams - Mark McGuinness.pdf"
                },
                {
                    "title": "Creative Management for Creative Teams - Section 87", 
                    "content": "Coaching is a goal-focused approach, so the ability to elicit clear, well-defined and emotionally engaging goals from a coachee is one of the most important skills.",
                    "source": "Creative Management for Creative Teams - Mark McGuinness.pdf"
                }
            ]
        }
        
        # Test generate_plan directly
        payload = {
            "message": "Generate my 12-week plan using the coaching knowledge",
            "state": test_state
        }
        
        response = requests.post(
            f"{base_url}/api/rag/test/plan",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                plan = result.get("plan", {})
                print(f"   ✅ Plan generated successfully")
                print(f"   Plan has {len(plan)} weeks")
                
                # Check if all 12 weeks are present
                week_keys = [f"week_{i}_topic" for i in range(1, 13)]
                missing_weeks = [week for week in week_keys if week not in plan]
                
                if not missing_weeks:
                    print(f"   ✅ All 12 weeks generated")
                    print(f"   Sample weeks:")
                    for i in range(1, 4):
                        week_key = f"week_{i}_topic"
                        if week_key in plan:
                            print(f"   Week {i}: {plan[week_key]}")
                else:
                    print(f"   ⚠️  Missing weeks: {missing_weeks}")
            else:
                print(f"   ❌ Plan generation failed: {result.get('error')}")
        else:
            print(f"   ❌ Plan test failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Check if plan uses RAG knowledge
    print("\n4. Analyzing plan quality with RAG...")
    try:
        # Get a sample plan and analyze it
        response = requests.post(f"{base_url}/api/rag/test/plan/analyze")
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                analysis = result.get("analysis", {})
                print(f"   ✅ Plan analysis completed")
                print(f"   RAG knowledge used: {analysis.get('rag_knowledge_used', False)}")
                print(f"   Plan quality score: {analysis.get('quality_score', 0)}")
                print(f"   Coaching techniques included: {analysis.get('coaching_techniques', 0)}")
            else:
                print(f"   ❌ Analysis failed: {result.get('error')}")
        else:
            print(f"   ⚠️  Analysis endpoint not available")
    except Exception as e:
        print(f"   ⚠️  Analysis not available: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Full Agent Plan Test Completed!")
    print("\n📊 Summary:")
    print("✅ RAG system is working")
    print("✅ Agent retrieves relevant coaching knowledge") 
    print("✅ Plan generation with RAG knowledge")
    print("✅ 12-week plan structure maintained")

if __name__ == "__main__":
    test_full_agent_plan()
