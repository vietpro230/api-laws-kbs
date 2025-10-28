from abc import ABC, abstractmethod
from langchain.chat_models import init_chat_model
from langchain.schema import HumanMessage, SystemMessage
from typing import Any, Optional
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
            model="google_genai:gemini-2.0-flash"
        )


    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        try:
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))

            result = self.model.invoke([messages])

            content = ""
            if result.generations and result.generations[0]:
                gen = result.generations[0][0]
                # Prefer message.content for chat models, fall back to text if present
                content = getattr(getattr(gen, "message", None), "content", None) or getattr(gen, "text", "")

            return content

        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return f"Error: {str(e)}"