"""
LangChain Memory Wrapper for OpenMemory
Integrates OpenMemory with LangChain's memory interface
"""

from typing import Any, Dict, List, Optional
from langchain.memory.chat_memory import BaseChatMemory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, get_buffer_string
from langchain_core.memory import BaseMemory
from pydantic import Field
import asyncio
import logging

from .openmemory import OpenMemoryClient

logger = logging.getLogger(__name__)


class OpenMemoryLangChain(BaseMemory):
    """
    LangChain memory backend using OpenMemory

    Provides persistent memory across sessions with:
    - Semantic search over past conversations
    - Multi-sector memory storage
    - Graph-based memory linking
    """

    client: OpenMemoryClient = Field(default=None)
    user_id: str = Field(default="default_user")
    memory_key: str = Field(default="chat_history")
    return_messages: bool = Field(default=True)
    input_key: Optional[str] = Field(default=None)
    output_key: Optional[str] = Field(default=None)
    max_context_messages: int = Field(default=10)
    min_similarity: float = Field(default=0.6)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.client is None:
            # Create default client
            from .openmemory import create_openmemory_client
            self.client = create_openmemory_client()

    @property
    def memory_variables(self) -> List[str]:
        """Return memory variables"""
        return [self.memory_key]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load memory variables

        Retrieves relevant memories based on the current input
        """
        try:
            # Get the input text
            input_text = inputs.get(self.input_key or "input", "")

            # Search for relevant memories
            loop = asyncio.get_event_loop()
            memories = loop.run_until_complete(
                self.client.search_memories(
                    query=input_text,
                    user_id=self.user_id,
                    limit=self.max_context_messages,
                    min_similarity=self.min_similarity
                )
            )

            if self.return_messages:
                # Convert to message format
                messages = []
                for mem in memories:
                    content = mem.get("content", "")
                    metadata = mem.get("metadata", {})

                    # Determine message type from metadata
                    if metadata.get("type") == "human":
                        messages.append(HumanMessage(content=content))
                    elif metadata.get("type") == "ai":
                        messages.append(AIMessage(content=content))

                return {self.memory_key: messages}
            else:
                # Return as string buffer
                text = "\n".join([m.get("content", "") for m in memories])
                return {self.memory_key: text}

        except Exception as e:
            logger.error(f"Failed to load memories: {e}")
            return {self.memory_key: [] if self.return_messages else ""}

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """
        Save context to OpenMemory

        Stores both input and output as separate memories
        """
        try:
            loop = asyncio.get_event_loop()

            # Save human input
            input_text = inputs.get(self.input_key or "input", "")
            if input_text:
                loop.run_until_complete(
                    self.client.add_memory(
                        content=input_text,
                        user_id=self.user_id,
                        metadata={"type": "human", "timestamp": None},
                        sector="episodic"
                    )
                )

            # Save AI output
            output_text = outputs.get(self.output_key or "output", "")
            if output_text:
                loop.run_until_complete(
                    self.client.add_memory(
                        content=output_text,
                        user_id=self.user_id,
                        metadata={"type": "ai", "timestamp": None},
                        sector="semantic"
                    )
                )

        except Exception as e:
            logger.error(f"Failed to save context: {e}")

    def clear(self) -> None:
        """Clear memory (not implemented for OpenMemory - requires manual deletion)"""
        logger.warning("Clear operation not implemented for OpenMemory")


class OpenMemoryChatMemory(BaseChatMemory):
    """
    Chat memory using OpenMemory with full message history support
    """

    client: OpenMemoryClient = Field(default=None)
    user_id: str = Field(default="default_user")
    max_context_messages: int = Field(default=20)
    min_similarity: float = Field(default=0.6)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.client is None:
            from .openmemory import create_openmemory_client
            self.client = create_openmemory_client()

    @property
    def memory_variables(self) -> List[str]:
        """Memory variables"""
        return [self.memory_key]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Load relevant chat history from OpenMemory"""
        try:
            input_text = inputs.get("input", "")

            loop = asyncio.get_event_loop()
            memories = loop.run_until_complete(
                self.client.search_memories(
                    query=input_text,
                    user_id=self.user_id,
                    limit=self.max_context_messages,
                    min_similarity=self.min_similarity
                )
            )

            messages = []
            for mem in memories:
                content = mem.get("content", "")
                metadata = mem.get("metadata", {})

                if metadata.get("type") == "human":
                    messages.append(HumanMessage(content=content))
                elif metadata.get("type") == "ai":
                    messages.append(AIMessage(content=content))

            if self.return_messages:
                return {self.memory_key: messages}
            else:
                return {self.memory_key: get_buffer_string(messages)}

        except Exception as e:
            logger.error(f"Failed to load chat memory: {e}")
            return {self.memory_key: [] if self.return_messages else ""}

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save conversation to OpenMemory"""
        try:
            loop = asyncio.get_event_loop()

            # Save human message
            input_text = inputs.get(self.input_key, "")
            if input_text:
                loop.run_until_complete(
                    self.client.add_memory(
                        content=input_text,
                        user_id=self.user_id,
                        metadata={"type": "human"},
                        sector="episodic"
                    )
                )

            # Save AI message
            output_text = outputs.get(self.output_key, "")
            if output_text:
                loop.run_until_complete(
                    self.client.add_memory(
                        content=output_text,
                        user_id=self.user_id,
                        metadata={"type": "ai"},
                        sector="semantic"
                    )
                )

        except Exception as e:
            logger.error(f"Failed to save chat context: {e}")

    def clear(self) -> None:
        """Clear memory (requires manual deletion in OpenMemory)"""
        logger.warning("Clear operation not supported for OpenMemory")
