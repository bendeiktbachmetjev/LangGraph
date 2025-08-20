import os
import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class LLMClient:
    """Client for interacting with OpenAI LLM"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4"  # Using GPT-4 as specified in requirements
    
    def call_llm(self, prompt: str) -> str:
        """
        Call OpenAI LLM with the given prompt and return JSON response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a mentor and must fully act like one. Always follow these rules:\n"
                            "1. You MUST ALWAYS respond ONLY in valid JSON format. This is CRITICAL.\n"
                            "2. When faced with inappropriate messages, redirect the conversation toward personal growth and understanding the user’s mistakes.\n"
                            "3. Avoid giving financial or medical advice.\n"
                            "4. If faced with ambiguity or provocation, gently steer the dialogue back to the core goal—exploring the roots of the behavior and guiding correction.\n"
                            "5. In any unclear situation, always remember: you are a mentor. Respond as a coach—guide the person, seek understanding, and lead them toward growth and self-correction.\n"
                            "6. Where a reply is needed, shortly (1 sentence) reflect on the user's message.\n"
                            "7. Provide ALL YOUR OUTPUTS ONLY IN JSON FORMAT."
                        )
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract the response content
            llm_response = response.choices[0].message.content.strip()
            logger.info(f"LLM response received: {llm_response[:100]}...")
            
            return llm_response
            
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            raise ValueError(f"Failed to get response from LLM: {e}")
    
    def validate_json_response(self, response: str) -> bool:
        """
        Validate that LLM response is valid JSON
        """
        try:
            json.loads(response)
            return True
        except json.JSONDecodeError:
            return False

# Global LLM client instance
llm_client = LLMClient() 