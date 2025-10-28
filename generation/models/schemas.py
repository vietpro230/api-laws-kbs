from pydantic import BaseModel
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph.message import add_messages


class GenerationRequest(BaseModel):
    prompt: str

class GenerationResponse(BaseModel):
    result: str
    status: str

class State(TypedDict, total=False):
    # Core message history
    messages: Annotated[list, add_messages]

    # Query processing fields
    query: str
    refined_query: str
    route: str

    # Search result fields
    top_docs: List[Dict[str, Any]]

    # Error handling
    error: Optional[str]
