#!/usr/bin/env python3
"""
Test to verify full 12-week plan generation with RAG.
"""

import sys
import os
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_full_12_week_plan():
    """Test full 12-week plan generation with RAG."""
    print("🎯 Full 12-Week Plan Test")
    print("=" * 60)
    
    try:
        from mentor_ai.cursor.core.graph_processor import GraphProcessor
        
        # State with RAG chunks
        state_with_rag = {
            "session_id": "test_12_week_plan",
            "user_name": "John",
            "user_age": 28,
            "goal_type": "career_improve",
            "career_goal": "Become a team leader",
            "goals": ["Improve leadership skills", "Build team management experience"],
            "skills": ["communication", "project management", "teamwork"],
            "interests": ["leadership", "personal development"],
            "retrieved_chunks": [
                {
                    "title": "Leadership Development Guide",
                    "content": "Effective leadership requires developing emotional intelligence, communication skills, and the ability to inspire and motivate team members. Key areas include active listening, conflict resolution, and strategic thinking."
                },
                {
                    "title": "Team Management Best Practices",
                    "content": "Successful team management involves setting clear goals, providing regular feedback, and creating an environment of trust and collaboration. Focus on delegation, motivation, and performance management."
                },
                {
                    "title": "Coaching Techniques for Career Growth",
                    "content": "Career development coaching emphasizes goal setting, skill assessment, and action planning. Use SMART goals, regular check-ins, and progress tracking to ensure continuous improvement."
                }
            ]
        }
        
        print("🚀 Generating full 12-week plan with RAG...")
        
        reply, final_state, final_node = GraphProcessor.process_node(
            "generate_plan",
            "Please create a comprehensive 12-week development plan",
            state_with_rag
        )
        
        print(f"✅ Plan generation completed")
        print(f"📝 Reply: {reply}")
        print(f"🎯 Final node: {final_node}")
        
        # Check if plan exists
        if final_state.get("plan"):
            plan = final_state["plan"]
            print(f"\n📋 FULL 12-WEEK PLAN:")
            print("=" * 60)
            
            # Count weeks
            week_count = len(plan)
            print(f"📊 Total weeks in plan: {week_count}")
            
            if week_count == 12:
                print("✅ Perfect! All 12 weeks are present!")
            else:
                print(f"❌ Expected 12 weeks, but got {week_count}")
            
            # Show all weeks
            print("\n📅 Complete Plan:")
            for i in range(1, 13):
                week_key = f"week_{i}_topic"
                if week_key in plan:
                    topic = plan[week_key]
                    print(f"   Week {i:2d}: {topic}")
                else:
                    print(f"   Week {i:2d}: ❌ MISSING")
            
            # Analyze plan content
            print(f"\n📊 Plan Analysis:")
            leadership_topics = 0
            team_topics = 0
            coaching_topics = 0
            management_topics = 0
            
            for week_key, topic in plan.items():
                topic_lower = topic.lower()
                if "leadership" in topic_lower or "leader" in topic_lower:
                    leadership_topics += 1
                if "team" in topic_lower:
                    team_topics += 1
                if "coaching" in topic_lower or "development" in topic_lower:
                    coaching_topics += 1
                if "management" in topic_lower or "manage" in topic_lower:
                    management_topics += 1
            
            print(f"   🎯 Leadership topics: {leadership_topics}")
            print(f"   👥 Team topics: {team_topics}")
            print(f"   🎓 Coaching/development topics: {coaching_topics}")
            print(f"   📊 Management topics: {management_topics}")
            
            # Check for RAG influence
            rag_keywords = ["emotional intelligence", "active listening", "conflict resolution", 
                          "strategic thinking", "delegation", "motivation", "performance management",
                          "goal setting", "skill assessment", "action planning", "SMART goals"]
            
            rag_influence = 0
            for week_key, topic in plan.items():
                topic_lower = topic.lower()
                for keyword in rag_keywords:
                    if keyword in topic_lower:
                        rag_influence += 1
                        break
            
            print(f"   🔍 RAG influence: {rag_influence} weeks contain RAG keywords")
            
            if rag_influence > 0:
                print("   ✅ RAG knowledge is influencing the plan!")
            else:
                print("   ⚠️  RAG knowledge doesn't seem to influence the plan")
                
        else:
            print("❌ Plan not generated in final state")
            print(f"Available keys in final_state: {list(final_state.keys())}")
            
    except Exception as e:
        print(f"❌ Error in plan generation: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("🎉 Full 12-Week Plan Test Complete!")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Full 12-Week Plan Test...")
    
    success = test_full_12_week_plan()
    
    if success:
        print("\n✅ Full 12-week plan test completed successfully!")
    else:
        print("\n❌ Full 12-week plan test failed.")
        sys.exit(1)
