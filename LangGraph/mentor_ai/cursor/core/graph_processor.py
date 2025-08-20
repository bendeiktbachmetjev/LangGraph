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
            
            # Update state
            updated_state = StateManager.update_state(current_state, llm_data, node)
            logger.info(f"State updated for session: {current_state.get('session_id')}")
            
            # Determine next node
            next_node = StateManager.get_next_node(llm_data, node, updated_state)
            logger.info(f"Next node: {next_node}")
            
            return llm_data["reply"], updated_state, next_node
            
        except Exception as e:
            logger.error(f"Error processing node {node_id}: {e}")
            raise 