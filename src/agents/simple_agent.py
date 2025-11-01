"""
Simple LangChain ReAct Agent
A straightforward ReAct (Reasoning + Acting) agent using LangChain
"""

from typing import Optional, Dict, Any, List
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseLanguageModel
from langchain.memory import ConversationBufferMemory
import logging
import json
from langchain.tools import Tool
logger = logging.getLogger(__name__)


# ReAct prompt template
REACT_PROMPT = """You are an AI HR Assistant helping with recruitment tasks.

You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Previous conversation:
{chat_history}

Question: {input}
Thought: {agent_scratchpad}"""


class SimpleReActAgent:
    """
    Simple ReAct Agent using LangChain

    Features:
    - ReAct prompting (Reasoning + Acting)
    - Simple conversation memory
    - Tool usage with clear reasoning
    - Easy to understand and debug
    """

    def __init__(
        self,
        llm: BaseLanguageModel,
        tools: List[BaseTool],
        memory: Optional[Any] = None,
        verbose: bool = True,
        max_iterations: int = 5,
        max_execution_time: Optional[float] = None
    ):
        """
        Initialize Simple ReAct Agent

        Args:
            llm: Language model
            tools: List of tools available to agent
            memory: Memory instance (default: ConversationBufferMemory)
            verbose: Enable verbose output
            max_iterations: Maximum reasoning iterations
            max_execution_time: Maximum execution time in seconds
        """
        self.llm = llm
        self.tools = tools
        self.verbose = verbose

        # Create memory if not provided
        if memory is None:
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="output"
            )
        else:
            self.memory = memory

        # Create prompt
        self.prompt = PromptTemplate.from_template(REACT_PROMPT)

        # Convert Tools to String-Based Format for ReAct
        wrapped_tools = [self.wrap_tool_for_react(t) if t.args_schema else t for t in tools]

        # Create agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=wrapped_tools,
            prompt=self.prompt
        )

        # Create agent executor
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=wrapped_tools,
            memory=self.memory,
            verbose=self.verbose,
            max_iterations=max_iterations,
            max_execution_time=max_execution_time,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )

        logger.info(f"Simple ReAct Agent initialized with {len(tools)} tools")

    def invoke(self, input_text: str) -> Dict[str, Any]:
        """
        Run the agent with an input

        Args:
            input_text: User input

        Returns:
            Agent response with output and intermediate steps
        """
        try:
            result = self.executor.invoke({"input": input_text})
            return {
                "output": result.get("output", ""),
                "intermediate_steps": result.get("intermediate_steps", []),
                "success": True
            }
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return {
                "output": f"Error: {str(e)}",
                "intermediate_steps": [],
                "success": False
            }

    async def ainvoke(self, input_text: str) -> Dict[str, Any]:
        """
        Run the agent asynchronously

        Args:
            input_text: User input

        Returns:
            Agent response
        """
        try:
            result = await self.executor.ainvoke({"input": input_text})
            return {
                "output": result.get("output", ""),
                "intermediate_steps": result.get("intermediate_steps", []),
                "success": True
            }
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return {
                "output": f"Error: {str(e)}",
                "intermediate_steps": [],
                "success": False
            }
        
    def wrap_tool_for_react(self, tool: BaseTool) -> Tool:
        """Wrap a structured tool to accept string inputs"""
        def wrapper(input_str: str):
            # Try to parse as JSON if tool has args_schema
            if tool.args_schema:
                try:
                    args = json.loads(input_str)
                    return tool.run(args)
                except (json.JSONDecodeError, ValueError) as e:
                    # Invalid JSON, try as direct input
                    return tool.run(input_str)
            return tool.run(input_str)

        return Tool(
            name=tool.name,
            description=tool.description,
            func=wrapper
        )
    def stream(self, input_text: str):
        """
        Stream agent execution

        Args:
            input_text: User input

        Yields:
            Chunks of agent execution
        """
        try:
            for chunk in self.executor.stream({"input": input_text}):
                yield chunk
        except Exception as e:
            logger.error(f"Agent streaming failed: {e}")
            yield {"error": str(e)}

    def clear_memory(self):
        """Clear conversation memory"""
        if hasattr(self.memory, 'clear'):
            self.memory.clear()
        logger.info("Memory cleared")

    def get_memory_summary(self) -> str:
        """Get a summary of current memory"""
        if hasattr(self.memory, 'load_memory_variables'):
            mem_vars = self.memory.load_memory_variables({})
            return str(mem_vars)
        return "No memory available"


def create_simple_react_agent(
    llm: BaseLanguageModel,
    tools: List[BaseTool],
    memory_type: str = "buffer",
    memory_config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> SimpleReActAgent:
    """
    Factory function to create a Simple ReAct Agent

    Args:
        llm: Language model
        tools: List of tools
        memory_type: Type of memory ("buffer", "summary", "openmemory")
        memory_config: Memory configuration
        **kwargs: Additional arguments for agent

    Returns:
        Configured SimpleReActAgent
    """
    # Create memory based on type
    if memory_type == "buffer":
        from langchain.memory import ConversationBufferMemory
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )

    elif memory_type == "summary":
        from langchain.memory import ConversationSummaryMemory
        memory = ConversationSummaryMemory(
            llm=llm,
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )

    elif memory_type == "openmemory":
        from src.memory.openmemory_langchain import OpenMemoryLangChain
        config = memory_config or {}
        memory = OpenMemoryLangChain(
            user_id=config.get("user_id", "default_user"),
            memory_key="chat_history",
            return_messages=True,
            **config
        )

    else:
        raise ValueError(f"Unknown memory type: {memory_type}")

    return SimpleReActAgent(
        llm=llm,
        tools=tools,
        memory=memory,
        **kwargs
    )
