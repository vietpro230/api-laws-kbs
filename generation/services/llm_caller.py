from abc import ABC, abstractmethod
from typing import Optional
import logging

from langchain.chat_models import init_chat_model
from langchain.schema import HumanMessage, SystemMessage, AIMessage

# Module logger
logger = logging.getLogger("generation.llm_caller")
if not logger.handlers:
    logger.addHandler(logging.NullHandler())


class LLMCaller(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response from prompt"""
        pass


class GeminiLLMCaller(LLMCaller):
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

            # Preferred simple content attribute
            if hasattr(result, "content") and isinstance(getattr(result, "content"), str):
                logger.debug("LLM returned content attribute")
                return result.content

            # LangChain newer-style generations
            if hasattr(result, "generations"):
                try:
                    if result.generations and result.generations[0]:
                        gen = result.generations[0][0]
                        content = (
                            getattr(getattr(gen, "message", None), "content", None)
                            or getattr(gen, "text", "")
                        )
                        logger.debug("LLM returned generations content")
                        return content
                except Exception:
                    logger.exception("Failed to extract from generations")

            # Direct AIMessage instance
            if isinstance(result, AIMessage):
                logger.debug("LLM returned AIMessage")
                return getattr(result, "content", str(result))

            # Fallback for list-like results
            if isinstance(result, list) and len(result) > 0:
                first = result[0]
                if hasattr(first, "content"):
                    logger.debug("LLM returned list with content")
                    return first.content
                return str(first)

            logger.debug("LLM returned fallback string")
            return str(result)

        except Exception as e:
            logger.exception("Error generating response: %s", str(e))
            return f"Error: {str(e)}"