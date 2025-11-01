"""
Agent state definitions for LangGraph
"""
from typing import TypedDict
from typing_extensions import Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage


class AgentState(TypedDict):
    """State schema for the HR agent"""
    messages: Annotated[list[AnyMessage], add_messages]
    sender_phone: str
    sender_identifier: str
