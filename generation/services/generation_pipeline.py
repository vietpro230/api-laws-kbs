import os
from timeit import default_timer as timer
from typing import List
from dotenv import load_dotenv
from .prompt_builder import DefaultPromptBuilder
from .llm_caller import GeminiLLMCaller
from langchain.schema import HumanMessage
from .search_relevant_laws import retrieve_relevant_laws


class GenerationService:
    def __init__(self):
        # Load environment variables
        load_dotenv(".env")

        # Get API key from environment
        api_key = os.getenv("GOOGLE_API_KEY")
        print(f"api_key loaded: {api_key is not None}")

        # Initialize components
        self.prompt_builder = DefaultPromptBuilder()
        # GeminiLLMCaller instance - use its generate() method
        self.llm_caller = GeminiLLMCaller(api_key)
        self.semantic_search = retrieve_relevant_laws

    def generate(self, query: str) -> str:
        data = self.semantic_search(
            query=query,
            n_resources_to_return=3,
            print_time=True
        )
        prompt = self.prompt_builder.build_prompt(query, data)
        # Use the LLM caller wrapper to generate answer
        answer = self.llm_caller.generate(prompt)

        return {'answer': answer, 'status': 'success'}





