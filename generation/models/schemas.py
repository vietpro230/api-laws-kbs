from pydantic import BaseModel
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph.message import add_messages


class GenerationRequest(BaseModel):
    # Use `query` as the field name because the route and service expect `body.query`.
    # Keep backwards-compatibility by allowing `prompt` as an alias if callers send it.
    query: str

    class Config:
        fields = {"query": {"alias": "prompt"}}

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
