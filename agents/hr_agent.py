from typing import List
from typing_extensions import TypedDict
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage, AnyMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from config import settings
from agents.prompts import SYSTEM_PROMPT
from mcp import (
    list_tools, execute_tool,
    SequentialThinkingTool,
    CVSheetManagerTool,
    GmailMCPTool,
    CalendarMCPTool,
    WebexMCPTool,
    DateTimeMCPTool,
    CVProcessTool,
    SearchCandidatesTool,
    SearchCreateSheetTool
)
from mcp.base import mcp_registry

class AgentState(TypedDict):
    messages: List[AnyMessage]
    sender_phone: str
    sender_identifier: str

def create_agent():
    """Create the LangGraph agent with MCP tools"""
    llm = ChatGoogleGenerativeAI(
        model=settings.MODEL_NAME,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=settings.TEMPERATURE
    )

    # Register all MCP tools
    mcp_registry.register(SequentialThinkingTool())
    mcp_registry.register(CVSheetManagerTool())
    mcp_registry.register(GmailMCPTool())
    mcp_registry.register(CalendarMCPTool())
    mcp_registry.register(WebexMCPTool())
    mcp_registry.register(DateTimeMCPTool())
    mcp_registry.register(CVProcessTool())
    mcp_registry.register(SearchCandidatesTool())
    mcp_registry.register(SearchCreateSheetTool())

    # Agent uses ONLY execute_tool - list_tools will be called manually if needed
    # We don't bind list_tools because it would confuse the LLM
    tools = [execute_tool]
    llm_with_tools = llm.bind_tools(tools)

    def agent_node(state: AgentState) -> AgentState:
        messages = state["messages"]
        if not any(isinstance(msg, SystemMessage) for msg in messages):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

        # Filter out any empty messages before sending to LLM
        filtered_messages = []
        for msg in messages:
            if isinstance(msg, ToolMessage):
                # Ensure ToolMessage has content
                if msg.content and msg.content.strip():
                    filtered_messages.append(msg)
            elif isinstance(msg, (SystemMessage, HumanMessage, AIMessage)):
                # Only add if message has content
                if hasattr(msg, 'content') and msg.content:
                    filtered_messages.append(msg)
                # AIMessage with tool_calls but no content is OK
                elif isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls') and msg.tool_calls:
                    filtered_messages.append(msg)

        response = llm_with_tools.invoke(filtered_messages)
        return {"messages": messages + [response]}

    def tool_node(state: AgentState) -> AgentState:
        messages = state["messages"]
        last_message = messages[-1]
        if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
            return state
        tool_messages = []
        for tool_call in last_message.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            tool_func = None
            for t in tools:
                if t.name == tool_name:
                    tool_func = t
                    break
            if tool_func:
                try:
                    result = tool_func.invoke(tool_args)
                    # Ensure result is not empty
                    result_str = str(result) if result else '{"status": "completed"}'
                    tool_messages.append(ToolMessage(
                        content=result_str,
                        tool_call_id=tool_call['id']
                    ))
                except Exception as e:
                    # If tool execution fails, return error message
                    tool_messages.append(ToolMessage(
                        content=f'{{"error": "{str(e)}"}}',
                        tool_call_id=tool_call['id']
                    ))
            else:
                # Tool not found
                tool_messages.append(ToolMessage(
                    content=f'{{"error": "Tool {tool_name} not found"}}',
                    tool_call_id=tool_call['id']
                ))
        return {"messages": messages + tool_messages}

    def should_continue(state: AgentState) -> str:
        messages = state["messages"]
        last_message = messages[-1]
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        return "end"

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", tool_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", "end": END})
    graph.add_edge("tools", "agent")
    return graph.compile()
