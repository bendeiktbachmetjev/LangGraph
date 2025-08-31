import logging
from typing import Dict, Any, Tuple
from .root_graph import Node, root_graph
from .prompting import generate_llm_prompt
from .llm_client import llm_client
from .state_manager import StateManager

logger = logging.getLogger(__name__)

class GraphProcessor:
    """Processes graph nodes by coordinating LLM calls and state updates"""
    
    @staticmethod
    def process_node(
        node_id: str, 
        user_message: str, 
        current_state: Dict[str, Any]
    ) -> Tuple[str, Dict[str, Any], str]:
        """
        Process a single graph node:
        1. Generate prompt for LLM
        2. Call LLM
        3. Parse response
        4. Update state
        5. Determine next node
        
        Returns: (reply, updated_state, next_node)
        """
        try:
            # Get the current node
            if node_id not in root_graph:
                raise ValueError(f"Unknown node: {node_id}")
            
            node = root_graph[node_id]
            logger.info(f"Processing node: {node_id}")
            
            # Check if node has an executor (non-LLM node)
            if node.executor:
                logger.info(f"Executing non-LLM node: {node_id}")
                llm_data = node.executor(user_message, current_state)
                logger.debug(f"Executor result: {llm_data}")
            else:
                # Generate prompt for LLM
                prompt = generate_llm_prompt(node, current_state, user_message)
                logger.debug(f"Generated prompt: {prompt[:200]}...")
                
                # Call LLM
                llm_response = llm_client.call_llm(prompt)
                logger.debug(f"LLM response: {llm_response}")
                
                # Parse LLM response
                llm_data = StateManager.parse_llm_response(llm_response, node)
                logger.debug(f"Parsed LLM data: {llm_data}")
            
            # Update state with assistant reply only (user message already processed in endpoint)
            updated_state = StateManager.update_state_with_memory(
                current_state, llm_data, node, 
                user_message=None,  # User message already processed
                assistant_reply=llm_data.get("reply", "")
            )
            logger.info(f"State updated with assistant reply for session: {current_state.get('session_id')}")
            
            # Log memory statistics for monitoring
            memory_stats = StateManager.get_memory_stats(updated_state)
            logger.info(f"Memory stats: {memory_stats}")
            
            # Determine next node
            next_node = StateManager.get_next_node(llm_data, node, updated_state)
            logger.info(f"Next node: {next_node}")
            
            return llm_data["reply"], updated_state, next_node
            
        except Exception as e:
            logger.error(f"Error processing node {node_id}: {e}")
            raise
    
    @staticmethod
    def process_node_with_memory_control(
        node_id: str, 
        user_message: str, 
        current_state: Dict[str, Any],
        use_memory: bool = True
    ) -> Tuple[str, Dict[str, Any], str]:
        """
        Process a single graph node with optional memory control:
        1. Generate prompt for LLM (with or without memory optimization)
        2. Call LLM
        3. Parse response
        4. Update state (with or without memory management)
        5. Determine next node
        
        Args:
            node_id: ID of the node to process
            user_message: User's message
            current_state: Current session state
            use_memory: Whether to use memory optimization (default: True)
            
        Returns: (reply, updated_state, next_node)
        """
        try:
            # Get the current node
            if node_id not in root_graph:
                raise ValueError(f"Unknown node: {node_id}")
            
            node = root_graph[node_id]
            logger.info(f"Processing node: {node_id} (memory: {use_memory})")
            
            # Check if node has an executor (non-LLM node)
            if node.executor:
                logger.info(f"Executing non-LLM node: {node_id}")
                llm_data = node.executor(user_message, current_state)
                logger.debug(f"Executor result: {llm_data}")
            else:
                # Generate prompt for LLM (with or without memory optimization)
                if use_memory:
                    prompt = generate_llm_prompt(node, current_state, user_message)
                else:
                    # Use fallback method for backward compatibility
                    from .prompting import generate_llm_prompt_with_history
                    prompt = generate_llm_prompt_with_history(node, current_state, user_message)
                
                logger.debug(f"Generated prompt: {prompt[:200]}...")
                
                # Call LLM
                llm_response = llm_client.call_llm(prompt)
                logger.debug(f"LLM response: {llm_response}")
                
                # Parse LLM response
                llm_data = StateManager.parse_llm_response(llm_response, node)
                logger.debug(f"Parsed LLM data: {llm_data}")
            
            # Update state (with or without memory management)
            if use_memory:
                updated_state = StateManager.update_state_with_memory(
                    current_state, llm_data, node, 
                    user_message=user_message, 
                    assistant_reply=llm_data.get("reply", "")
                )
                logger.info(f"State updated with memory for session: {current_state.get('session_id')}")
                
                # Log memory statistics for monitoring
                memory_stats = StateManager.get_memory_stats(updated_state)
                logger.info(f"Memory stats: {memory_stats}")
            else:
                updated_state = StateManager.update_state(current_state, llm_data, node)
                logger.info(f"State updated without memory for session: {current_state.get('session_id')}")
            
            # Determine next node
            next_node = StateManager.get_next_node(llm_data, node, updated_state)
            logger.info(f"Next node: {next_node}")
            
            return llm_data["reply"], updated_state, next_node
            
        except Exception as e:
            logger.error(f"Error processing node {node_id}: {e}")
            raise
    
    @staticmethod
    def get_memory_stats(current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get memory statistics for the current state
        
        Args:
            current_state: Current session state
            
        Returns:
            Dictionary with memory statistics
        """
        return StateManager.get_memory_stats(current_state) 