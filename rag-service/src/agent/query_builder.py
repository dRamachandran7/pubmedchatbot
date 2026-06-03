import logging
from typing import Dict, List, Any
import json
import requests
from ..config.prompts import QUERY_BUILDER_PROMPT

logger = logging.getLogger(__name__)


class QueryBuilderAgent:
    """Transforms natural language queries into optimized PubMed search queries"""
    
    def __init__(self, model: str = "llama2", ollama_url: str = "http://localhost:11434"):
        self.model = model
        self.ollama_url = ollama_url
    
    def build_query(self, user_prompt: str) -> Dict[str, Any]:
        """
        Convert user's natural language prompt into optimized PubMed search queries
        
        Args:
            user_prompt: The user's natural language question/request
        
        Returns:
            {
                "primary_query": str,  # Main PubMed search query
                "alternative_queries": list,  # Alternative search queries
                "search_strategy": str,  # Explanation of search strategy
                "key_terms": list,  # Important medical terms identified
                "success": bool,  # Whether query building was successful
                "error": str or None  # Error message if failed
            }
        """
        prompt = f"{QUERY_BUILDER_PROMPT}\nUser Question: {user_prompt}"
        
        try:
            logger.info(f"Building search query for: {user_prompt}")
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama error: {response.status_code} - {response.text}")
                return self._default_response(user_prompt)
            
            response_text = response.json().get("response", "")
            logger.debug(f"Raw Ollama response: {response_text[:300]}")
            
            # Try to parse as JSON
            try:
                json_result = json.loads(response_text)
                json_result["success"] = True
                json_result["error"] = None
                logger.info(f"Successfully built queries: {json_result.get('primary_query')}")
                return json_result
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON response: {e}")
                # Try to extract JSON from the response
                try:
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}') + 1
                    if start_idx != -1 and end_idx > start_idx:
                        json_str = response_text[start_idx:end_idx]
                        json_result = json.loads(json_str)
                        json_result["success"] = True
                        json_result["error"] = None
                        return json_result
                except Exception as inner_e:
                    logger.warning(f"Failed to extract JSON: {inner_e}")
                return self._default_response(user_prompt)
                    
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return self._default_response(user_prompt)
        except Exception as e:
            logger.error(f"Unexpected error in build_query: {e}")
            return self._default_response(user_prompt)
    
    def _default_response(self, user_prompt: str) -> Dict[str, Any]:
        """Fallback response when LLM fails"""
        # Simple fallback: use user prompt as primary query
        return {
            "primary_query": user_prompt,
            "alternative_queries": [],
            "search_strategy": "Fallback: Using user prompt directly as search query",
            "key_terms": [],
            "success": False,
            "error": "Failed to optimize query, using original prompt"
        }
