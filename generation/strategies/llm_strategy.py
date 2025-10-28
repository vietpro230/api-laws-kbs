"""Base LLM strategy interface"""
from abc import ABC, abstractmethod

class LLMStrategy(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate response from prompt"""
        pass