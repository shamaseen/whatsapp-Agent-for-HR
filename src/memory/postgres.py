"""
LangGraph-native memory management using PostgreSQL checkpointer.
This replaces the old custom ConversationMemory with LangGraph's built-in system.
"""

from typing import Optional
from langgraph.checkpoint.postgres import PostgresSaver
from src.config import settings
import psycopg


class LangGraphMemory:
    """
    LangGraph-native memory management using PostgreSQL checkpointer.

    Features:
    - Automatic conversation persistence
    - Built-in state management
    - Thread-safe connection management
    - Efficient querying
    - Native LangGraph integration
    """

    def __init__(self):
        """Initialize PostgreSQL checkpointer"""
        self._checkpointer: Optional[PostgresSaver] = None
        self._conn: Optional[psycopg.Connection] = None
        self._setup_done = False

    def _ensure_checkpointer(self):
        """Create checkpointer and setup tables if not exists"""
        if self._checkpointer is None:
            db_url = settings.DATABASE_URL

            try:
                # First, ensure tables exist using a temporary connection
                temp_conn = psycopg.connect(db_url, autocommit=True, prepare_threshold=None)
                temp_checkpointer = PostgresSaver(temp_conn)
                try:
                    temp_checkpointer.setup()
                    print("✅ LangGraph PostgreSQL checkpointer tables initialized")
                except Exception as setup_error:
                    if "already exists" in str(setup_error).lower() or "task_path" in str(setup_error).lower():
                        print("✅ Checkpointer tables already exist")
                    else:
                        raise
                finally:
                    temp_conn.close()

                # Now create the persistent connection for actual use
                self._conn = psycopg.connect(
                    db_url,
                    autocommit=True,
                    prepare_threshold=None,
                )
                self._checkpointer = PostgresSaver(self._conn)
                self._setup_done = True
                print(f"✅ Checkpointer ready with autocommit=True")

            except Exception as e:
                print(f"❌ Error setting up checkpointer: {e}")
                if self._conn:
                    self._conn.close()
                    self._conn = None
                raise

    def get_checkpointer(self) -> PostgresSaver:
        """
        Get PostgreSQL checkpointer with persistent connection.
        
        Returns a PostgresSaver that maintains a single database connection.
        This connection is reused for all checkpointing operations.

        Returns:
            PostgresSaver instance for LangGraph
        """
        self._ensure_checkpointer()
        return self._checkpointer

    async def get_checkpointer_async(self) -> PostgresSaver:
        """
        Async version of get_checkpointer.

        Returns:
            PostgresSaver instance for async LangGraph
        """
        return self.get_checkpointer()

    def close(self):
        """Close database connection"""
        if self._conn:
            self._conn.close()
            self._conn = None
        self._checkpointer = None
        self._setup_done = False


# Global memory instance
langgraph_memory = LangGraphMemory()


def get_checkpointer() -> PostgresSaver:
    """
    Get the global checkpointer instance.
    Use this in your agent creation.

    Example:
        from src.memory.postgres import get_checkpointer

        agent = graph.compile(checkpointer=get_checkpointer())

    Returns:
        PostgresSaver instance
    """
    return langgraph_memory.get_checkpointer()


async def get_checkpointer_async() -> PostgresSaver:
    """
    Async version of get_checkpointer.

    Returns:
        PostgresSaver instance
    """
    return await langgraph_memory.get_checkpointer_async()


def get_conversation_history(thread_id: str, limit: int = 10):
    """
    Get conversation history for a thread (compatibility function).

    Note: With LangGraph checkpointing, you don't usually need this.
    The agent automatically loads history based on thread_id.

    Args:
        thread_id: Thread/session ID
        limit: Number of messages (not used with checkpointer)

    Returns:
        Message history (handled by checkpointer internally)
    """
    return {
        "info": "History is managed by LangGraph checkpointer",
        "usage": "Pass thread_id in config when invoking agent",
        "example": {
            "thread_id": thread_id,
            "config": {"configurable": {"thread_id": thread_id}}
        }
    }


def verify_checkpointer():
    """
    Verify that the checkpointer is working correctly.
    This will print the status of the checkpointer connection.
    """
    try:
        checkpointer = get_checkpointer()
        print("✅ Checkpointer initialized successfully")
        print(f"   Connection status: {'open' if checkpointer.conn and not checkpointer.conn.closed else 'closed'}")
        return True
    except Exception as e:
        print(f"❌ Checkpointer verification failed: {e}")
        return False


def migrate_from_old_memory():
    """
    Migration helper: Explains how to migrate from old ConversationMemory.

    Old way:
        memory = ConversationMemory(session_id)
        memory.add_message("user", "Hello")
        history = memory.get_history()

    New way:
        from src.memory.postgres import get_checkpointer

        # In agent creation:
        agent = graph.compile(checkpointer=get_checkpointer())

        # When invoking:
        config = {"configurable": {"thread_id": session_id}}
        result = agent.invoke({"messages": [...]}, config=config)

        # History is automatically managed!
    """
    pass