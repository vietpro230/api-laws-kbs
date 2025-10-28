"""Domain models"""
from pydantic import BaseModel
from typing import List

class Law(BaseModel):
    """Law domain model"""
    title: str
    content: str
    articles: List[str]