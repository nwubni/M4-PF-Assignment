from pydantic import BaseModel
from typing import List, Optional


class SubQuery(BaseModel):
    """Model for a sub-query in a multi-part query."""

    query: str
    category: str
    agent: str


class MultiQueryModel(BaseModel):
    """Model for multi-part query decomposition."""

    is_multi_query: bool
    sub_queries: List[SubQuery] = []
    original_query: str
