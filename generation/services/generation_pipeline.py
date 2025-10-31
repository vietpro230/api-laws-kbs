import os
import logging
import traceback
from timeit import default_timer as timer
from typing import List
from dotenv import load_dotenv
from .prompt_builder import DefaultPromptBuilder
from .llm_caller import GeminiLLMCaller
from langchain.schema import HumanMessage
from .search_relevant_laws import retrieve_relevant_laws

# Logger for generation pipeline
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
logger = logging.getLogger("generation.pipeline")
if not logger.handlers:
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    fh = logging.FileHandler(os.path.join(LOG_DIR, "generation_pipeline.log"), encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(sh)
    logger.addHandler(fh)
logger.info("Logger configured for generation.pipeline")


class GenerationService:
    def __init__(self):
        try:
            # Load environment variables
            load_dotenv(".env")

            # Get API key from environment
            api_key = os.getenv("GOOGLE_API_KEY")
            logger.info("api_key loaded: %s", api_key is not None)

            # Initialize components
            self.prompt_builder = DefaultPromptBuilder()
            self.llm_caller = GeminiLLMCaller(api_key)
            self.semantic_search = retrieve_relevant_laws
            logger.info("GenerationService initialized.")
        except Exception as e:
            logger.exception("Failed to initialize GenerationService: %s", str(e))
            raise

    def generate(self, query: str) -> str:
        try:
            logger.info("Starting generation for query: %s", query)
            logger.info("Exec`uting semantic search for query: '%s'", query)
            start_time = timer()
            data = self.semantic_search(
                query=query,
                n_resources_to_return=3,
                print_time=True
            )
            end_time = timer()
            logger.info("Semantic search completed in %.2f seconds, returned %d items",
                       end_time - start_time, len(data))

            logger.info("Building prompt with retrieved data")
            prompt = self.prompt_builder.build_prompt(query, data)
            logger.debug("Built prompt (len=%d)", len(prompt))

            # Use the LLM caller wrapper to generate answer
            answer = self.llm_caller.generate(prompt)
            logger.info("LLM generated answer (len=%d)", len(answer) if isinstance(answer, str) else 0)

            return {'answer': answer, 'status': 'success'}
        except Exception as e:
            tb = traceback.format_exc()
            logger.error("Generation failed: %s\n%s", str(e), tb)
            return {'answer': f'Error: {str(e)}', 'status': 'error', 'error': str(e), 'traceback': tb}





