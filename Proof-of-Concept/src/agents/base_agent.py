import os
from typing import Optional
from openai import OpenAI
from src.utils.config import FIREWORKS_API_KEY
from src.utils.logger import setup_logger

logger = setup_logger("base-agent")

def get_fireworks_client() -> Optional[OpenAI]:
    """Retrieves an initialized OpenAI client for Fireworks if the API key is present, else None."""
    api_key = FIREWORKS_API_KEY or os.getenv("FIREWORKS_API_KEY")
    if not api_key:
        logger.warning("No FIREWORKS_API_KEY found. Agents will execute using offline clinical heuristics.")
        return None
        
    try:
        client = OpenAI(
            base_url="https://api.fireworks.ai/inference/v1",
            api_key=api_key
        )
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Fireworks client: {e}. Falling back to offline mode.")
        return None
