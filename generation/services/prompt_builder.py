"""Prompt building strategies"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class PromptBuilder(ABC):
    @abstractmethod
    def build_prompt(self, query: str, context: List[Dict]) -> str:
        pass

class DefaultPromptBuilder(PromptBuilder):
    def build_prompt(self, query: str, context: List[Dict]) -> str:
        try:
            print("[INFO] Building prompt with provided context.", context)
            if not query or not isinstance(query, str):
                raise ValueError("Query must be a non-empty string")

            if not context or not isinstance(context, list):
                raise ValueError("Context must be a non-empty list of law chunks")

            # Format each context chunk with its page number
            formatted_chunks = []
            for chunk in context:
                if not isinstance(chunk, dict):
                    continue

                text = chunk.get("sentence_chunk", "")
                page = chunk.get("page_number", "")
                if text and page:
                    formatted_chunks.append(f"[Page {page}] {text}")

            if not formatted_chunks:
                raise ValueError("No valid law chunks found in context")

            # Build the complete prompt
            context_str = "\n\n".join(formatted_chunks)
            prompt = f"""Bạn là một trợ lý trả lời câu hỏi pháp luật; chỉ sử dụng các đoạn trích luật được cung cấp bên dưới.

                    Ngữ cảnh (đoạn trích luật):
                    {context_str}

                    Câu hỏi:
                    {query}

                    Hướng dẫn:
                    1. Bạn là 1 chuyên gia pháp luật Việt Nam.
                    2. Nếu câu hỏi không rõ ràng hoặc thiếu thông tin, trước tiên hãy yêu cầu làm rõ thay vì đoán.
                    3. Với những câu hỏi rõ ràng, trả lời ngắn gọn, chính xác và mạch lạc.
                    4. Nếu câu hỏi liên quan đến pháp luật Việt Nam, căn cứ hoàn toàn vào văn bản pháp luật hiện hành có trong ngữ cảnh
                    5. Luôn trích dẫn các trang cụ thể từ ngữ cảnh bằng định dạng {page} trong câu trả lời của bạn."""
            return prompt

        except Exception as e:
            print(f"[ERROR] Failed to build prompt: {str(e)}")
            raise