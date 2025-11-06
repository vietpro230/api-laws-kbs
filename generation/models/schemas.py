from pydantic import BaseModel


class GenerationRequest(BaseModel):
    query: str
    custom_prompt: str = None

class GenerationResponse(BaseModel):
    result: str
    status: str
