import logging
from typing import Dict, Any, List
from datetime import datetime, timezone
from .llm_client import llm_client

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages conversation memory and token optimization"""
    
    @staticmethod
    def update_prompt_context(state: Dict[str, Any], new_message: dict) -> Dict[str, Any]:
        """
        Update prompt_context with new message while preserving history
        
        Args:
            state: Current session state
            new_message: New message to add ({"role": "user"|"assistant", "content": str})
            
        Returns:
            Updated state with new prompt_context
        """
        updated_state = state.copy()
        
        # Initialize prompt_context if not exists
        if "prompt_context" not in updated_state:
            updated_state["prompt_context"] = {
                "running_summary": None,
                "recent_messages": [],
                "important_facts": [],
                "weekly_summaries": {}
            }
        
        # Add message to recent_messages
        recent = updated_state["prompt_context"].get("recent_messages", [])
        recent.append(new_message)
        
        # Keep only last 5 messages
        if len(recent) > 5:
            recent = recent[-5:]
        
        # Increment message counter
        message_count = updated_state.get("message_count", 0) + 1
        
        # Update running summary every 20 messages
        if message_count % 20 == 0:
            running_summary = MemoryManager._create_running_summary(
                updated_state.get("history", [])
            )
            updated_state["prompt_context"]["running_summary"] = running_summary
            logger.info(f"Updated running summary for session {updated_state.get('session_id', 'unknown')}")
        
        # Update prompt_context
        updated_state["prompt_context"]["recent_messages"] = recent
        updated_state["message_count"] = message_count
        
        return updated_state
    
    @staticmethod
    def evaluate_important_facts(state: Dict[str, Any], message: dict) -> List[dict]:
        """
        Evaluate if message contains important facts
        
        Args:
            state: Current session state
            message: Message to evaluate
            
        Returns:
            List of important facts found in the message
        """
        # This will be implemented with LLM evaluation
        # For now, return empty list - will be enhanced in future versions
        return []
    
    @staticmethod
    def create_weekly_summary(session_id: str, state: Dict[str, Any], week_number: int) -> Dict[str, Any]:
        """
        Create weekly summary when transitioning between weeks
        
        Args:
            session_id: Session identifier
            state: Current session state
            week_number: Week number to summarize
            
        Returns:
            Weekly summary dictionary
        """
        current_history = state.get("history", [])
        current_facts = state.get("prompt_context", {}).get("important_facts", [])
        
        # Create summary using LLM
        summary_prompt = f"""
        Create a concise summary of Week {week_number} conversation.
        Focus on key insights, progress made, and important points discussed.
        
        Conversation history:
        {current_history}
        
        Important facts from this week:
        {current_facts}
        
        Provide a 2-3 sentence summary.
        """
        
        try:
            # Try to create summary using LLM
            summary_response = llm_client.call_llm(summary_prompt)
            summary = summary_response.strip()
            logger.info(f"Created weekly summary for week {week_number}, session {session_id}")
        except Exception as e:
            logger.error(f"Failed to create weekly summary with LLM: {e}")
            # Fallback: create a basic summary from conversation history
            if current_history:
                # Extract key points from conversation
                user_messages = [msg.get('content', '') for msg in current_history if msg.get('role') == 'user']
                assistant_messages = [msg.get('content', '') for msg in current_history if msg.get('role') == 'assistant']
                
                # Create a simple summary
                summary = f"Week {week_number} summary: User engaged in {len(user_messages)} conversations. Key topics discussed: {', '.join(user_messages[:3]) if user_messages else 'No specific topics'}"
            else:
                summary = f"Week {week_number} conversation summary"
        
        weekly_summary = {
            "summary": summary,
            "important_facts": [f for f in current_facts if f.get('week') == week_number],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "message_count": state.get("message_count", 0)
        }
        
        return weekly_summary
    
    @staticmethod
    def _create_running_summary(history: List[dict]) -> str:
        """
        Create running summary from conversation history
        
        Args:
            history: List of conversation messages
            
        Returns:
            Brief summary of recent conversation
        """
        if not history:
            return "No conversation history yet."
        
        # Create summary prompt
        conversation_text = "\n".join([
            f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
            for msg in history[-20:]  # Last 20 messages
        ])
        
        summary_prompt = f"""
        Create a brief 1-2 sentence summary of this conversation segment.
        Focus on the main topic and key points discussed.
        
        Conversation:
        {conversation_text}
        
        Summary:
        """
        
        try:
            summary_response = llm_client.call_llm(summary_prompt)
            return summary_response.strip()
        except Exception as e:
            logger.error(f"Failed to create running summary: {e}")
            return "Conversation summary unavailable."
    
    @staticmethod
    def format_prompt_context(state: Dict[str, Any]) -> str:
        """
        Format prompt_context for inclusion in LLM prompt
        
        Args:
            state: Current session state
            
        Returns:
            Formatted string for inclusion in LLM prompt
        """
        prompt_context = state.get("prompt_context", {})
        if not prompt_context:
            return ""
        
        context_sections = []
        
        # Running summary
        running_summary = prompt_context.get("running_summary")
        if running_summary:
            context_sections.append(f"Running Summary: {running_summary}")
        
        # Recent messages
        recent_messages = prompt_context.get("recent_messages", [])
        if recent_messages:
            recent_text = "\n".join([
                f"{msg.get('role', 'unknown')}: {msg.get('content', '')}"
                for msg in recent_messages
            ])
            context_sections.append(f"Recent Messages:\n{recent_text}")
        
        # Important facts
        important_facts = prompt_context.get("important_facts", [])
        if important_facts:
            facts_text = "\n".join([
                f"- {fact.get('fact', '')} (Week {fact.get('week', 0)})"
                for fact in important_facts[-10:]  # Last 10 facts
            ])
            context_sections.append(f"Important Facts:\n{facts_text}")
        
        # Weekly summaries
        weekly_summaries = prompt_context.get("weekly_summaries", {})
        if weekly_summaries:
            summaries_text = "\n".join([
                f"Week {week}: {summary.get('summary', '')}"
                for week, summary in weekly_summaries.items()
            ])
            context_sections.append(f"Weekly Summaries:\n{summaries_text}")
        
        return "\n\n".join(context_sections)
    
    @staticmethod
    def get_token_estimate(state: Dict[str, Any]) -> int:
        """
        Estimate token usage for current prompt_context
        
        Args:
            state: Current session state
            
        Returns:
            Estimated token count
        """
        prompt_context = state.get("prompt_context", {})
        if not prompt_context:
            return 0
        
        # Rough token estimation (4 characters ≈ 1 token)
        total_chars = 0
        
        # Running summary
        running_summary = prompt_context.get("running_summary", "")
        if running_summary:
            total_chars += len(running_summary)
        
        # Recent messages
        recent_messages = prompt_context.get("recent_messages", [])
        for msg in recent_messages:
            total_chars += len(msg.get("content", ""))
        
        # Important facts
        important_facts = prompt_context.get("important_facts", [])
        for fact in important_facts:
            total_chars += len(str(fact))
        
        # Weekly summaries
        weekly_summaries = prompt_context.get("weekly_summaries", {})
        for summary in weekly_summaries.values():
            total_chars += len(summary.get("summary", ""))
        
        # Convert to estimated tokens
        estimated_tokens = total_chars // 4
        
        return estimated_tokens
    
    @staticmethod
    def initialize_prompt_context() -> Dict[str, Any]:
        """
        Initialize empty prompt_context structure
        
        Returns:
            Empty prompt_context dictionary
        """
        return {
            "running_summary": None,
            "recent_messages": [],
            "important_facts": [],
            "weekly_summaries": {}
        }
    
    @staticmethod
    def add_important_fact(state: Dict[str, Any], fact: dict) -> Dict[str, Any]:
        """
        Add important fact to prompt_context
        
        Args:
            state: Current session state
            fact: Fact to add ({"fact": str, "week": int, "importance_score": float})
            
        Returns:
            Updated state with new fact
        """
        updated_state = state.copy()
        
        # Initialize prompt_context if not exists
        if "prompt_context" not in updated_state:
            updated_state["prompt_context"] = MemoryManager.initialize_prompt_context()
        
        # Add fact with timestamp
        fact_with_timestamp = {
            **fact,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        updated_state["prompt_context"]["important_facts"].append(fact_with_timestamp)
        
        # Keep only last 20 facts to prevent bloat
        if len(updated_state["prompt_context"]["important_facts"]) > 20:
            updated_state["prompt_context"]["important_facts"] = \
                updated_state["prompt_context"]["important_facts"][-20:]
        
        return updated_state
    
    @staticmethod
    def get_memory_stats(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get memory system statistics
        
        Args:
            state: Current session state
            
        Returns:
            Dictionary with memory statistics
        """
        prompt_context = state.get("prompt_context", {})
        
        return {
            "message_count": state.get("message_count", 0),
            "current_week": state.get("current_week", 1),
            "running_summary_exists": prompt_context.get("running_summary") is not None,
            "recent_messages_count": len(prompt_context.get("recent_messages", [])),
            "important_facts_count": len(prompt_context.get("important_facts", [])),
            "weekly_summaries_count": len(prompt_context.get("weekly_summaries", {})),
            "history_count": len(state.get("history", []))
        }
