"""
Agent state for the bank application.
"""

import operator
from typing import Annotated, TypedDict
from typing import Sequence

from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """
    Agent state for the bank application.
    """

    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str
    result: dict
