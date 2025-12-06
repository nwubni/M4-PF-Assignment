"""
Agent state for the bank application.
"""

from typing import Annotated, TypedDict
import operator
from langchain_core.messages import BaseMessage
from typing import Sequence


class AgentState(TypedDict):
    """
    Agent state for the bank application.
    """

    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
    result: dict

