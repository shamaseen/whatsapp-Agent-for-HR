"""
MCP Sequential Thinking Tool
Provides AI reasoning and planning capabilities before taking actions
"""

from typing import Dict, Any
from .base import MCPTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from config import settings


class SequentialThinkingTool(MCPTool):
    """
    MCP tool for sequential thinking and planning.
    Allows the agent to reason through complex tasks before executing them.
    """

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=settings.MODEL_NAME,
            google_api_key=settings.GOOGLE_API_KEY,
            temperature=0.3  # Lower temperature for more focused thinking
        )
        super().__init__()

    def get_name(self) -> str:
        return "sequential_thinking"

    def get_description(self) -> str:
        return """Use this tool to think through complex tasks step-by-step before taking actions.

This tool helps you:
1. Break down user requests into subtasks
2. Plan the execution sequence
3. Identify required tools and dependencies
4. Consider edge cases and potential issues
5. Validate your reasoning

Always use this tool FIRST for complex operations involving multiple steps or tools."""

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "The task or user request to think through"
                },
                "context": {
                    "type": "string",
                    "description": "Additional context about the current situation (optional)"
                },
                "available_tools": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of available tools (from list_tools output)"
                }
            },
            "required": ["task"]
        }

    def execute(self, task: str, context: str = "", available_tools: list = None) -> str:
        """
        Execute sequential thinking process

        Args:
            task: The task to think through
            context: Additional context
            available_tools: List of available tool names

        Returns:
            Structured thinking output with execution plan
        """
        tools_info = ""
        if available_tools:
            tools_info = f"\n\nAvailable tools: {', '.join(available_tools)}"

        prompt = f"""You are an AI assistant helping to plan task execution. Think through the following task carefully and systematically.

**Task:** {task}

**Context:** {context if context else "None provided"}
{tools_info}

Please provide a structured analysis with:

1. **Task Understanding**: What is the user asking for?
2. **Required Steps**: Break down the task into ordered steps
3. **Tool Selection**: Which tools are needed for each step?
4. **Dependencies**: What information from previous steps is needed?
5. **Edge Cases**: What could go wrong? How to handle it?
6. **Validation**: How to verify success?
7. **Execution Plan**: Clear sequence of actions to take

Be specific and actionable. Your thinking will guide the agent's actions."""

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            return f"Error in thinking process: {str(e)}"
