from abc import ABC, abstractmethod
from typing import Optional
import logging

from langchain.chat_models import init_chat_model
from langchain.schema import HumanMessage, SystemMessage, AIMessage
class LLMStrategy(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate response from prompt"""
        pass


# Module logger
logger = logging.getLogger("generation.llm_caller")
if not logger.handlers:
    logger.addHandler(logging.NullHandler())


class GeminiLLMCaller(LLMStrategy):
    def __init__(self, api_key: str):
        # Fixed: Added required model parameter
        self.model = init_chat_model(
            api_key=api_key,
            model="google_genai:gemini-2.0-flash",
        )

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        try:
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))

            logger.debug("Invoking LLM with %d messages", len(messages))
            result = self.model.invoke(messages)
            if hasattr(result, "content") and isinstance(getattr(result, "content"), str):
                logger.debug("LLM returned content attribute")
                return result.content

            return str(result)

        except Exception as e:
            logger.exception("Error generating response: %s", str(e))
            return f"Error: {str(e)}"