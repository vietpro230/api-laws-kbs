from abc import ABC, abstractmethod
from typing import Optional

class LLMStrategy(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate response from prompt"""
        pass

    @abstractmethod
    def stream(self, prompt: str) -> str:
        """Streaming response from prompt"""
        pass

