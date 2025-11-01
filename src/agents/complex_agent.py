"""
Complex LangGraph Agent
Advanced agent with multi-node graph, conditional routing, and sophisticated memory
"""

from typing import List, Dict, Any, Optional, Annotated, TypedDict, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseLanguageModel
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.base import BaseCheckpointSaver
import operator
import logging

logger = logging.getLogger(__name__)


# Define agent state with proper annotations
class AgentState(TypedDict):
    """State for the complex LangGraph agent"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_task: Optional[str]
    tool_outputs: Dict[str, Any]
    iteration_count: int
    needs_clarification: bool
    reflection: Optional[str]


class ComplexLangGraphAgent:
    """
    Complex LangGraph Agent with:
    - Multi-node workflow graph
    - Conditional routing based on agent decisions
    - Reflection and self-critique capabilities
    - Tool usage with error handling
    - Memory persistence via checkpointer
    - Human-in-the-loop support
    - Gemini-compatible message handling
    """

    def __init__(
        self,
        llm: BaseLanguageModel,
        tools: List[BaseTool],
        checkpointer: Optional[BaseCheckpointSaver] = None,
        system_prompt: Optional[str] = None,
        max_iterations: int = 10,
        enable_reflection: bool = True,
        verbose: bool = True
    ):
        """
        Initialize Complex LangGraph Agent

        Args:
            llm: Language model
            tools: List of tools
            checkpointer: Checkpoint saver for memory persistence
            system_prompt: System prompt for the agent
            max_iterations: Maximum iterations
            enable_reflection: Enable reflection node
            verbose: Verbose output
        """
        self.llm = llm
        self.tools = tools
        self.checkpointer = checkpointer
        self.max_iterations = max_iterations
        self.enable_reflection = enable_reflection
        self.verbose = verbose

        self.system_prompt = system_prompt or self._default_system_prompt()

        # Create tool node
        self.tool_node = ToolNode(tools)

        # Build the graph
        self.graph = self._build_graph()

        logger.info(f"Complex LangGraph Agent initialized with {len(tools)} tools")

    def _default_system_prompt(self) -> str:
        """Default system prompt"""
        return """You are an advanced AI HR Assistant with expertise in recruitment.

You have access to powerful tools for managing candidates, scheduling interviews,
sending emails, and analyzing CVs.

Your workflow:
1. Understand the user's request clearly
2. Plan your approach step-by-step
3. Use tools when needed to gather information or take action
4. Reflect on your actions and adjust if needed
5. Provide clear, helpful responses

Always be professional, thorough, and proactive."""

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        graph = StateGraph(AgentState)

        # Add nodes
        graph.add_node("planner", self._planner_node)
        graph.add_node("executor", self._executor_node)
        graph.add_node("tools", self.tool_node)

        if self.enable_reflection:
            graph.add_node("reflector", self._reflector_node)

        graph.add_node("responder", self._responder_node)

        # Set entry point
        graph.set_entry_point("planner")

        # Add edges
        graph.add_conditional_edges(
            "planner",
            self._should_continue_to_executor,
            {
                "executor": "executor",
                "responder": "responder"
            }
        )

        graph.add_conditional_edges(
            "executor",
            self._route_after_executor,
            {
                "tools": "tools",
                "reflector": "reflector" if self.enable_reflection else "responder",
                "responder": "responder"
            }
        )

        graph.add_edge("tools", "reflector" if self.enable_reflection else "responder")

        if self.enable_reflection:
            graph.add_conditional_edges(
                "reflector",
                self._should_continue_after_reflection,
                {
                    "executor": "executor",
                    "responder": "responder"
                }
            )

        graph.add_edge("responder", END)

        # Compile with checkpointer
        return graph.compile(checkpointer=self.checkpointer)

    def _format_messages_for_llm(self, messages: List[BaseMessage], system_content: Optional[str] = None) -> List[BaseMessage]:
        """
        Format messages properly for LLM invocation (especially Gemini)

        Args:
            messages: List of messages
            system_content: Optional system message content

        Returns:
            Properly formatted message list
        """
        formatted = []
        
        # Add system message if provided
        if system_content:
            formatted.append(SystemMessage(content=system_content))
        
        # Filter and format user messages
        for msg in messages:
            if isinstance(msg, (HumanMessage, AIMessage)):
                # Ensure content is not empty (content can be string or list)
                if msg.content:
                    # Handle both string and list content types
                    if isinstance(msg.content, str):
                        if msg.content.strip():
                            formatted.append(msg)
                    elif isinstance(msg.content, list) and msg.content:
                        formatted.append(msg)
            elif isinstance(msg, SystemMessage) and not system_content:
                # Only add system messages if we didn't already add one
                if msg.content:
                    # Handle both string and list content types
                    if isinstance(msg.content, str):
                        if msg.content.strip():
                            formatted.append(msg)
                    elif isinstance(msg.content, list) and msg.content:
                        formatted.append(msg)
        
        # Ensure we have at least one message
        if not formatted:
            formatted.append(HumanMessage(content="Hello"))
        
        return formatted

    def _invoke_llm_safely(self, messages: List[BaseMessage], system_content: Optional[str] = None) -> AIMessage:
        """
        Safely invoke LLM with proper error handling

        Args:
            messages: Messages to send
            system_content: Optional system prompt

        Returns:
            AI response message
        """
        try:
            formatted_messages = self._format_messages_for_llm(messages, system_content)
            response = self.llm.invoke(formatted_messages)
            
            # Ensure response has content
            if not response.content:
                response.content = "I understand. How can I help you?"
            
            return response
        except Exception as e:
            logger.error(f"LLM invocation failed: {e}", exc_info=True)
            return AIMessage(content=f"Error communicating with LLM: {str(e)}")

    def _planner_node(self, state: AgentState) -> Dict[str, Any]:
        """Planning node - analyzes request and creates plan"""
        messages = list(state["messages"])

        # Get the user's request
        user_request = ""
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                user_request = msg.content
                break

        # Create planning prompt
        planning_prompt = f"""{self.system_prompt}

Analyze the user's request and create a step-by-step plan.

User request: {user_request}

Available tools: {', '.join([t.name for t in self.tools])}

Respond with:
1. Your understanding of the request
2. Your step-by-step plan
3. Which tools you'll need to use"""

        response = self._invoke_llm_safely(messages, planning_prompt)

        if self.verbose:
            logger.info(f"Plan created: {response.content[:200]}...")

        return {
            "messages": [response],
            "current_task": "planning_complete",
            "iteration_count": 0
        }

    def _executor_node(self, state: AgentState) -> Dict[str, Any]:
        """Executor node - decides on actions and tool usage"""
        messages = list(state["messages"])
        iteration = state.get("iteration_count", 0)

        # Check iteration limit
        if iteration >= self.max_iterations:
            return {
                "current_task": "max_iterations_reached"
            }

        # Create executor prompt
        executor_prompt = f"""Based on the plan and current progress, what should you do next?

Available tools: {', '.join([t.name for t in self.tools])}

Options:
1. Use a tool (specify tool name and inputs)
2. Request more information from user
3. Provide final answer

Respond in this format:
ACTION: [use_tool | request_info | final_answer]
TOOL: [tool_name] (if ACTION is use_tool)
INPUT: [tool_input] (if ACTION is use_tool)
REASONING: [your reasoning]"""

        response = self._invoke_llm_safely(messages, executor_prompt)

        # Parse response to determine next action
        # Handle case where content might be a list or string
        content_str = ""
        if isinstance(response.content, str):
            content_str = response.content.lower()
        elif isinstance(response.content, list):
            # Join list elements into string
            content_str = " ".join(str(c) for c in response.content).lower()
        else:
            content_str = str(response.content).lower()

        if "use_tool" in content_str:
            current_task = "use_tool"
            needs_clarification = False
        elif "request_info" in content_str:
            current_task = "request_info"
            needs_clarification = True
        else:
            current_task = "final_answer"
            needs_clarification = False

        return {
            "messages": [response],
            "current_task": current_task,
            "iteration_count": iteration + 1,
            "needs_clarification": needs_clarification
        }

    def _reflector_node(self, state: AgentState) -> Dict[str, Any]:
        """Reflection node - critiques and improves responses"""
        messages = list(state["messages"])

        reflection_prompt = """Review your recent actions and outputs.

Questions to consider:
1. Did you achieve the goal?
2. Were the tool outputs accurate and helpful?
3. Is there anything you should do differently?
4. Do you need to take additional actions?

Provide a brief reflection and next steps."""

        response = self._invoke_llm_safely(messages, reflection_prompt)

        if self.verbose:
            logger.info(f"Reflection: {response.content[:200]}...")

        reflection_message = AIMessage(content=f"[Reflection: {response.content}]")

        return {
            "messages": [reflection_message],
            "reflection": response.content
        }

    def _responder_node(self, state: AgentState) -> Dict[str, Any]:
        """Responder node - generates final response"""
        messages = list(state["messages"])

        response_prompt = """Generate a clear, helpful final response to the user.

Include:
1. Summary of what you did
2. Key findings or results
3. Next steps or recommendations
4. Any relevant information from tool outputs

Be conversational and professional."""

        response = self._invoke_llm_safely(messages, response_prompt)

        return {
            "messages": [response],
            "current_task": "complete"
        }

    # Conditional routing functions
    def _should_continue_to_executor(self, state: AgentState) -> str:
        """Decide if we should go to executor or skip to responder"""
        try:
            messages = state.get("messages", [])
            if not messages:
                return "responder"

            # Handle both string and list content types
            content = messages[-1].content
            if isinstance(content, str):
                last_message = content.lower()
            elif isinstance(content, list):
                last_message = " ".join(str(c) for c in content).lower()
            else:
                last_message = str(content).lower()

            if any(tool.name.lower() in last_message for tool in self.tools):
                return "executor"
        except Exception as e:
            logger.warning(f"Routing decision error: {e}")

        return "responder"

    def _route_after_executor(self, state: AgentState) -> str:
        """Route after executor based on current task"""
        task = state.get("current_task", "")

        if task == "use_tool":
            return "tools"
        elif task == "request_info":
            return "responder"
        elif task in ["final_answer", "max_iterations_reached"]:
            return "reflector" if self.enable_reflection else "responder"
        else:
            return "responder"

    def _should_continue_after_reflection(self, state: AgentState) -> str:
        """Decide if we need more iterations after reflection"""
        reflection = state.get("reflection", "").lower()
        iteration = state.get("iteration_count", 0)

        # Check if reflection suggests more work needed
        if iteration < self.max_iterations and ("need" in reflection or "should" in reflection):
            return "executor"

        return "responder"

    def invoke(self, input_text: str, thread_id: str = "default") -> Dict[str, Any]:
        """
        Run the agent

        Args:
            input_text: User input
            thread_id: Thread ID for memory persistence

        Returns:
            Agent response
        """
        try:
            initial_state = {
                "messages": [HumanMessage(content=input_text)],
                "current_task": None,
                "tool_outputs": {},
                "iteration_count": 0,
                "needs_clarification": False,
                "reflection": None
            }

            config = {"configurable": {"thread_id": thread_id}}

            result = self.graph.invoke(initial_state, config)

            # Extract final response
            messages = result.get("messages", [])
            final_message = messages[-1] if messages else AIMessage(content="No response generated")

            return {
                "output": final_message.content,
                "messages": messages,
                "iterations": result.get("iteration_count", 0),
                "reflection": result.get("reflection"),
                "success": True
            }

        except Exception as e:
            logger.error(f"Agent execution failed: {e}", exc_info=True)
            return {
                "output": f"Error: {str(e)}",
                "messages": [],
                "iterations": 0,
                "reflection": None,
                "success": False,
                "error": str(e)
            }

    async def ainvoke(self, input_text: str, thread_id: str = "default") -> Dict[str, Any]:
        """Async invoke"""
        try:
            initial_state = {
                "messages": [HumanMessage(content=input_text)],
                "current_task": None,
                "tool_outputs": {},
                "iteration_count": 0,
                "needs_clarification": False,
                "reflection": None
            }

            config = {"configurable": {"thread_id": thread_id}}

            result = await self.graph.ainvoke(initial_state, config)

            messages = result.get("messages", [])
            final_message = messages[-1] if messages else AIMessage(content="No response generated")

            return {
                "output": final_message.content,
                "messages": messages,
                "iterations": result.get("iteration_count", 0),
                "reflection": result.get("reflection"),
                "success": True
            }

        except Exception as e:
            logger.error(f"Agent execution failed: {e}", exc_info=True)
            return {
                "output": f"Error: {str(e)}",
                "messages": [],
                "iterations": 0,
                "reflection": None,
                "success": False,
                "error": str(e)
            }

    def stream(self, input_text: str, thread_id: str = "default"):
        """Stream agent execution"""
        try:
            initial_state = {
                "messages": [HumanMessage(content=input_text)],
                "current_task": None,
                "tool_outputs": {},
                "iteration_count": 0,
                "needs_clarification": False,
                "reflection": None
            }

            config = {"configurable": {"thread_id": thread_id}}

            for chunk in self.graph.stream(initial_state, config):
                yield chunk

        except Exception as e:
            logger.error(f"Agent streaming failed: {e}", exc_info=True)
            yield {"error": str(e), "success": False}


def create_complex_langgraph_agent(
    llm: BaseLanguageModel,
    tools: List[BaseTool],
    memory_type: str = "postgres",
    memory_config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> ComplexLangGraphAgent:
    """
    Factory function to create a Complex LangGraph Agent

    Args:
        llm: Language model
        tools: List of tools
        memory_type: Type of memory ("postgres", "sqlite", "memory")
        memory_config: Memory configuration
        **kwargs: Additional arguments

    Returns:
        Configured ComplexLangGraphAgent
    """
    checkpointer = None

    # Create checkpointer based on type
    if memory_type == "postgres":
        try:
            from src.memory.postgres import get_checkpointer
            checkpointer = get_checkpointer()
        except Exception as e:
            logger.warning(f"Failed to create postgres checkpointer: {e}")
            from langgraph.checkpoint.memory import MemorySaver
            checkpointer = MemorySaver()

    elif memory_type == "sqlite":
        from langgraph.checkpoint.sqlite import SqliteSaver
        config = memory_config or {}
        db_path = config.get("db_path", ":memory:")
        checkpointer = SqliteSaver.from_conn_string(db_path)

    elif memory_type == "memory":
        from langgraph.checkpoint.memory import MemorySaver
        checkpointer = MemorySaver()

    return ComplexLangGraphAgent(
        llm=llm,
        tools=tools,
        checkpointer=checkpointer,
        **kwargs
    )