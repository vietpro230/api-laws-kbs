import os
import pandas as pd
import numpy as np
import torch
from timeit import default_timer as timer
from typing import List
from dotenv import load_dotenv
from .prompt_builder import DefaultPromptBuilder
from .llm_caller import GeminiLLMCaller
from .response_processor import ResponseProcessor
from .citation_mapper import CitationMapper
from .validator import Validator
from sentence_transformers import SentenceTransformer, util
from .search_relevant_laws import retrieve_relevant_laws
from .build_graph import build_graph


class GenerationService:
    def __init__(self):
        # Load environment variables
        load_dotenv(".env")

        # Get API key from environment
        api_key = os.getenv("GOOGLE_API_KEY")
        print(f"api_key loaded: {api_key is not None}")

        # Initialize components
        self.prompt_builder = DefaultPromptBuilder()
        self.llm_caller = GeminiLLMCaller(api_key).model
        self.graph = build_graph(self.llm_caller)


    def generate(self, query: str) -> str:
        print("\n" + "=" * 50)
        print(f"New conversation turn: {query}")
        print("=" * 50)

        # Initialize state
        initial_state = {"messages": [{"role": "user", "content": query}]}

        # Process through graph
        last_msg = None
        for event in self.graph.stream(initial_state):
            for key, value in event.items():
                if isinstance(value, dict) and "messages" in value:
                    last_msg = value["messages"][-1]
                    if isinstance(last_msg, dict) and last_msg.get("role") == "assistant":
                        print("\nAssistant:", last_msg["content"])

        if not last_msg or not isinstance(last_msg, dict):
            raise ValueError("No valid response generated")
        print("\nFinal response generated.", last_msg.get("content", ""))
        return {
            "answer": last_msg.get("content", "No response generated"),
            "status": "success"
        }



