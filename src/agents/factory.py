"""
Agent Factory
Unified factory for creating different agent types with various memory options
"""

from typing import List, Dict, Any, Optional, Literal
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseLanguageModel
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AgentType(str, Enum):
    """Available agent types"""
    SIMPLE_REACT = "simple_react"
    COMPLEX_LANGGRAPH = "complex_langgraph"


class MemoryType(str, Enum):
    """Available memory types"""
    BUFFER = "buffer"  # Simple conversation buffer
    SUMMARY = "summary"  # Conversation summary
    POSTGRES = "postgres"  # PostgreSQL checkpointer (LangGraph)
    SQLITE = "sqlite"  # SQLite checkpointer (LangGraph)
    MEMORY_SAVER = "memory"  # In-memory checkpointer (LangGraph)
    OPENMEMORY = "openmemory"  # OpenMemory integration


class AgentFactory:
    """
    Factory for creating agents with different configurations

    Supports:
    - Simple ReAct agents (LangChain)
    - Complex LangGraph agents
    - Multiple memory backends
    - Easy switching between configurations
    """

    @staticmethod
    def create_agent(
        agent_type: AgentType,
        llm: BaseLanguageModel,
        tools: List[BaseTool],
        memory_type: MemoryType = MemoryType.BUFFER,
        memory_config: Optional[Dict[str, Any]] = None,
        agent_config: Optional[Dict[str, Any]] = None
    ):
        """
        Create an agent with specified configuration

        Args:
            agent_type: Type of agent to create
            llm: Language model
            tools: List of tools
            memory_type: Type of memory to use
            memory_config: Configuration for memory
            agent_config: Additional agent configuration

        Returns:
            Configured agent instance

        Example:
            >>> from src.agents.factory import AgentFactory, AgentType, MemoryType
            >>> agent = AgentFactory.create_agent(
            ...     agent_type=AgentType.SIMPLE_REACT,
            ...     llm=my_llm,
            ...     tools=my_tools,
            ...     memory_type=MemoryType.OPENMEMORY
            ... )
        """
        memory_config = memory_config or {}
        agent_config = agent_config or {}

        logger.info(f"Creating {agent_type} agent with {memory_type} memory")

        # Create appropriate agent
        if agent_type == AgentType.SIMPLE_REACT:
            return AgentFactory._create_simple_react_agent(
                llm, tools, memory_type, memory_config, agent_config
            )

        elif agent_type == AgentType.COMPLEX_LANGGRAPH:
            return AgentFactory._create_complex_langgraph_agent(
                llm, tools, memory_type, memory_config, agent_config
            )

        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

    @staticmethod
    def _create_simple_react_agent(
        llm, tools, memory_type, memory_config, agent_config
    ):
        """Create Simple ReAct agent"""
        from src.agents.simple_agent import create_simple_react_agent

        # Map memory types to simple agent compatible types
        if memory_type in [MemoryType.POSTGRES, MemoryType.SQLITE, MemoryType.MEMORY_SAVER]:
            logger.warning(f"Memory type {memory_type} not compatible with Simple ReAct agent, using buffer")
            memory_type = MemoryType.BUFFER

        # Convert to string value if it's an Enum
        memory_type_str = memory_type.value if hasattr(memory_type, 'value') else str(memory_type)

        return create_simple_react_agent(
            llm=llm,
            tools=tools,
            memory_type=memory_type_str,
            memory_config=memory_config,
            **agent_config
        )

    @staticmethod
    def _create_complex_langgraph_agent(
        llm, tools, memory_type, memory_config, agent_config
    ):
        """Create Complex LangGraph agent"""
        from src.agents.complex_agent import ComplexLangGraphAgent
        from src.memory.postgres import get_checkpointer

        # Get appropriate checkpointer based on memory type
        checkpointer = get_checkpointer()

        # Ensure checkpointer is not in agent_config to avoid duplicate argument
        filtered_config = {k: v for k, v in agent_config.items() if k != 'checkpointer'}

        return ComplexLangGraphAgent(
            llm=llm,
            tools=tools,
            checkpointer=checkpointer,
            **filtered_config
        )

    @staticmethod
    def get_recommended_memory(agent_type: AgentType) -> MemoryType:
        """
        Get recommended memory type for an agent type

        Args:
            agent_type: Agent type

        Returns:
            Recommended memory type
        """
        recommendations = {
            AgentType.SIMPLE_REACT: MemoryType.BUFFER,
            AgentType.COMPLEX_LANGGRAPH: MemoryType.POSTGRES
        }

        return recommendations.get(agent_type, MemoryType.BUFFER)

    @staticmethod
    def list_compatible_memories(agent_type: AgentType) -> List[MemoryType]:
        """
        List compatible memory types for an agent

        Args:
            agent_type: Agent type

        Returns:
            List of compatible memory types
        """
        compatibility = {
            AgentType.SIMPLE_REACT: [
                MemoryType.BUFFER,
                MemoryType.SUMMARY,
                MemoryType.OPENMEMORY
            ],
            AgentType.COMPLEX_LANGGRAPH: [
                MemoryType.POSTGRES,
                MemoryType.SQLITE,
                MemoryType.MEMORY_SAVER
            ]
        }

        return compatibility.get(agent_type, [])

    @staticmethod
    def get_agent_info(agent_type: AgentType) -> Dict[str, Any]:
        """
        Get information about an agent type

        Args:
            agent_type: Agent type

        Returns:
            Agent information
        """
        info = {
            AgentType.SIMPLE_REACT: {
                "name": "Simple ReAct Agent",
                "description": "Straightforward ReAct (Reasoning + Acting) agent",
                "features": [
                    "Clear reasoning steps",
                    "Simple conversation memory",
                    "Easy to understand and debug",
                    "Fast execution"
                ],
                "best_for": "Simple tasks, quick responses, debugging"
            },
            AgentType.COMPLEX_LANGGRAPH: {
                "name": "Complex LangGraph Agent",
                "description": "Advanced multi-node graph agent with reflection",
                "features": [
                    "Multi-node workflow graph",
                    "Conditional routing",
                    "Self-reflection and critique",
                    "Persistent memory via checkpointer",
                    "Error handling and recovery"
                ],
                "best_for": "Complex workflows, multi-step tasks, production use"
            }
        }

        return info.get(agent_type, {})

    @staticmethod
    def get_memory_info(memory_type: MemoryType) -> Dict[str, Any]:
        """
        Get information about a memory type

        Args:
            memory_type: Memory type

        Returns:
            Memory information
        """
        info = {
            MemoryType.BUFFER: {
                "name": "Conversation Buffer",
                "description": "Stores full conversation history in memory",
                "pros": ["Simple", "Fast", "Complete history"],
                "cons": ["Limited by context window", "No persistence"],
                "use_case": "Short conversations, testing"
            },
            MemoryType.SUMMARY: {
                "name": "Conversation Summary",
                "description": "Summarizes conversation to save tokens",
                "pros": ["Token efficient", "Handles long conversations"],
                "cons": ["May lose details", "Extra LLM calls"],
                "use_case": "Long conversations, token optimization"
            },
            MemoryType.POSTGRES: {
                "name": "PostgreSQL Checkpointer",
                "description": "Persistent storage in PostgreSQL",
                "pros": ["Persistent", "Scalable", "Multi-user"],
                "cons": ["Requires database", "More complex setup"],
                "use_case": "Production, multi-user applications"
            },
            MemoryType.SQLITE: {
                "name": "SQLite Checkpointer",
                "description": "Local file-based persistent storage",
                "pros": ["Persistent", "No external DB", "Simple"],
                "cons": ["Single-user", "File-based limitations"],
                "use_case": "Development, single-user apps"
            },
            MemoryType.MEMORY_SAVER: {
                "name": "In-Memory Checkpointer",
                "description": "Temporary in-memory storage",
                "pros": ["Fast", "Simple", "No setup"],
                "cons": ["Not persistent", "Lost on restart"],
                "use_case": "Testing, development, demos"
            },
            MemoryType.OPENMEMORY: {
                "name": "OpenMemory",
                "description": "Self-hosted AI memory engine with semantic search",
                "pros": [
                    "Semantic memory search",
                    "Multi-sector storage",
                    "Graph-based linking",
                    "Privacy-focused"
                ],
                "cons": ["Requires external service", "Additional setup"],
                "use_case": "Advanced memory needs, long-term recall"
            }
        }

        return info.get(memory_type, {})


# Convenience functions
def create_agent_from_config(config: Dict[str, Any]):
    """
    Create agent from configuration dictionary

    Args:
        config: Configuration with agent_type, memory_type, etc.

    Returns:
        Configured agent
    """
    from src.agents import get_tools

    # Get LLM
    from langchain_google_genai import ChatGoogleGenerativeAI
    from src.config import settings

    llm = ChatGoogleGenerativeAI(
        model=settings.MODEL_NAME,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=settings.TEMPERATURE
    )

    # Get tools
    tools = get_tools()

    return AgentFactory.create_agent(
        agent_type=AgentType(config.get("agent_type", "simple_react")),
        llm=llm,
        tools=tools,
        memory_type=MemoryType(config.get("memory_type", "buffer")),
        memory_config=config.get("memory_config", {}),
        agent_config=config.get("agent_config", {})
    )
