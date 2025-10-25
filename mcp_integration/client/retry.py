"""
Retry Logic for MCP Connections
Handles connection failures with exponential backoff
"""

import asyncio
from typing import Callable, Any, Optional
from functools import wraps


class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


async def retry_async(
    func: Callable,
    config: Optional[RetryConfig] = None,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable] = None
) -> Any:
    """
    Retry an async function with exponential backoff
    
    Args:
        func: Async function to retry
        config: Retry configuration (uses defaults if None)
        exceptions: Tuple of exceptions to catch and retry
        on_retry: Optional callback called on each retry (attempt, error)
    
    Returns:
        Result from successful function call
    
    Raises:
        Last exception if all retries fail
    """
    if config is None:
        config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(1, config.max_attempts + 1):
        try:
            return await func()
        
        except exceptions as e:
            last_exception = e
            
            if attempt >= config.max_attempts:
                # Last attempt failed - raise exception
                raise
            
            # Calculate delay with exponential backoff
            delay = min(
                config.base_delay * (config.exponential_base ** (attempt - 1)),
                config.max_delay
            )
            
            # Add jitter to prevent thundering herd
            if config.jitter:
                import random
                delay *= (0.5 + random.random() * 0.5)
            
            # Call retry callback if provided
            if on_retry:
                try:
                    await on_retry(attempt, e, delay)
                except Exception:
                    pass  # Don't let callback errors interrupt retry
            
            # Wait before retry
            print(f"   ⟳ Retry {attempt}/{config.max_attempts} after {delay:.1f}s: {str(e)}")
            await asyncio.sleep(delay)
    
    # Should never reach here, but just in case
    if last_exception:
        raise last_exception


def with_retry(
    config: Optional[RetryConfig] = None,
    exceptions: tuple = (Exception,)
):
    """
    Decorator to add retry logic to async functions
    
    Args:
        config: Retry configuration
        exceptions: Tuple of exceptions to retry on
    
    Example:
        @with_retry(config=RetryConfig(max_attempts=5))
        async def connect_to_server():
            # Connection logic here
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async def call_func():
                return await func(*args, **kwargs)
            
            return await retry_async(
                call_func,
                config=config,
                exceptions=exceptions
            )
        
        return wrapper
    
    return decorator


# Enhanced clients with retry logic

class RetryMixin:
    """Mixin to add retry capability to MCP clients"""
    
    def __init__(self, *args, retry_config: Optional[RetryConfig] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.retry_config = retry_config or RetryConfig()
    
    async def connect_with_retry(self) -> Any:
        """Connect with automatic retry on failure"""
        
        async def on_retry(attempt: int, error: Exception, delay: float):
            print(f"   ⟳ Connection retry {attempt}/{self.retry_config.max_attempts}")
            print(f"      Error: {str(error)}")
            print(f"      Waiting {delay:.1f}s before retry...")
        
        return await retry_async(
            func=self.connect,
            config=self.retry_config,
            exceptions=(ConnectionError, TimeoutError, OSError),
            on_retry=on_retry
        )


# Example usage in updated clients

"""
# In stdio_client.py - ADD RetryMixin:

from .retry import RetryMixin, RetryConfig

class StdioMCPClient(RetryMixin, BaseMCPClient):
    
    def __init__(self, server_name: str, config: Dict[str, Any]):
        retry_config = RetryConfig(
            max_attempts=config.get("retry_attempts", 3),
            base_delay=config.get("retry_delay", 1.0)
        )
        super().__init__(
            server_name=server_name,
            config=config,
            retry_config=retry_config
        )
        self._client_context = None
        self._session_context = None

# Then in tool_factory.py - USE connect_with_retry:

async def _load_mcp_server(self, server_name: str):
    try:
        client = create_mcp_client(server_name, config)
        
        # Use retry logic if client supports it
        if hasattr(client, 'connect_with_retry'):
            tools = await client.connect_with_retry()
        else:
            tools = await client.connect()
        
        self.mcp_clients[server_name] = client
        return tools
    except Exception as e:
        print(f"   ✗ Connection failed after retries: {e}")
        return await self._fallback_to_custom(server_name)
"""
