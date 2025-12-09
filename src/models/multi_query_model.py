"""

Multi-query decomposition models for sub-query and multi-query processing.

"""

from typing import List

from pydantic import BaseModel


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
