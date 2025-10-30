from abc import ABC, abstractmethod
from typing import Optional

from langchain.chat_models import init_chat_model
from langchain.schema import HumanMessage, SystemMessage, AIMessage


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

            result = self.model.invoke(messages)

            # Preferred simple content attribute
            if hasattr(result, "content") and isinstance(getattr(result, "content"), str):
                return result.content

            # LangChain newer-style generations
            if hasattr(result, "generations"):
                try:
                    if result.generations and result.generations[0]:
                        gen = result.generations[0][0]
                        # Prefer message.content for chat models, fall back to text if present
                        return (
                            getattr(getattr(gen, "message", None), "content", None)
                            or getattr(gen, "text", "")
                        )
                except Exception:
                    pass

            # Direct AIMessage instance
            if isinstance(result, AIMessage):
                return getattr(result, "content", str(result))

            # Fallback for list-like results
            if isinstance(result, list) and len(result) > 0:
                first = result[0]
                if hasattr(first, "content"):
                    return first.content
                return str(first)

            return str(result)

        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return f"Error: {str(e)}"