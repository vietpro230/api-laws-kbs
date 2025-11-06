"""Prompt building strategies"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from langchain.prompts import PromptTemplate
from pathlib import Path

class PromptBuilder(ABC):
    @abstractmethod
    def build_prompt(self, query: str, custom_prompt: Optional[str] = None) -> str:
        pass


class DefaultPromptBuilder(PromptBuilder):

    def __init__(self, default_prompt_path: str = "config/prompt/default.txt"):
        self.default_prompt_path = Path(default_prompt_path)

    def load_default_prompt(self) -> str:
        if not self.default_prompt_path.exists():
            raise FileNotFoundError(f"Default prompt file not found at {self.default_prompt_path}")
        with open(self.default_prompt_path, "r", encoding="utf-8") as f:
            return f.read()

    def build_prompt(self, query: str, custom_prompt: Optional[str] = None) -> str:
            try:
                if custom_prompt:
                    prompt_template = custom_prompt + "\n\nCâu hỏi:\n{query}"
                else:
                    prompt_template = self.load_default_prompt()

                prompt = PromptTemplate.from_template(prompt_template)
                final_prompt = prompt.format(query=query)

                return final_prompt.strip()

            except Exception as e:
                print(f"[ERROR] Failed to build prompt: {e}")
                raise