import os
import logging
import traceback
from timeit import default_timer as timer
from dotenv import load_dotenv
from .prompt_builder import DefaultPromptBuilder
from strategies.gemini_stragety import GeminiLLMCaller
from .search_relevant_laws import retrieve_relevant_laws
from config.settings import settings

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
            api_key = settings.GOOGLE_API_KEY
            logger.info("api_key loaded: %s", api_key is not None)

            # Initialize components
            self.prompt_builder = DefaultPromptBuilder()
            self.llm_caller = GeminiLLMCaller(api_key)
            # self.semantic_search = retrieve_relevant_laws
            logger.info("GenerationService initialized.")
        except Exception as e:
            logger.exception("Failed to initialize GenerationService: %s", str(e))
            raise

    def generate(self, query: str) -> str:
        try:
            logger.info("Starting generation for query: %s", query)
            start_time = timer()
            # data = self.semantic_search(
            #     query=query,
            #     n_resources_to_return=3,
            #     print_time=True
            # )
            # end_time = timer()
            # logger.info("Semantic search completed in %.2f seconds, returned %d items",
            #            end_time - start_time, len(data))

            # logger.info("Building prompt with retrieved data")
            # prompt = self.prompt_builder.build_prompt(query, data)

            # Use the LLM caller wrapper to generate answer
            answer = self.llm_caller.generate(query)
            logger.info("LLM generated answer (len=%d)", len(answer) if isinstance(answer, str) else 0)

            return {'answer': answer, 'status': 'success'}
        except Exception as e:
            tb = traceback.format_exc()
            logger.error("Generation failed: %s\n%s", str(e), tb)
            return {'answer': f'Error: {str(e)}', 'status': 'error', 'error': str(e), 'traceback': tb}

    def generate_stream(self, query: str):
        """Generator function for streaming responses"""
        try:
            logger.info("Starting streaming generation for query: %s", query)
            start_time = timer()

            # Semantic search
            data = self.semantic_search(
                query=query,
                n_resources_to_return=3,
                print_time=False
            )
            end_time = timer()
            logger.info("Search completed in %.2f seconds", end_time - start_time)

            prompt = self.prompt_builder.build_prompt(query, data)

            # Stream from LLM
            # Nếu llm_caller có method stream
            if hasattr(self.llm_caller, 'stream'):
                for chunk in self.llm_caller.stream(prompt):
                    yield chunk
            else:
                # Fallback: fake stream nếu LLM không hỗ trợ
                answer = self.llm_caller.generate(prompt)
                words = answer.split()
                for word in words:
                    yield word + " "

        except Exception as e:
            logger.error("Streaming generation failed: %s", str(e))
            yield f"Error: {str(e)}"



