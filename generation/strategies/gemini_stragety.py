from abc import ABC, abstractmethod
from typing import Optional
from langchain.chat_models import init_chat_model
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from strategies.llm_strategy import LLMStrategy


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


            result = self.model.invoke(messages)
            if hasattr(result, "content") and isinstance(getattr(result, "content"), str):
                return result.content

            return str(result)

        except Exception as e:
            return f"Error: {str(e)}"

    def stream(self, prompt: str, system_prompt: Optional[str] = None):
        """Generator function for streaming responses"""
        try:
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))

            # Sử dụng stream method của LangChain
            for chunk in self.model.stream(messages):
                if hasattr(chunk, "content") and chunk.content:
                    yield chunk.content
                elif isinstance(chunk, str):
                    yield chunk

        except Exception as e:
            yield f"Error: {str(e)}"
