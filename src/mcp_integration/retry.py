"""
Retry Logic for MCP Connections
Handles connection failures with exponential backoff
"""

import asyncio
import random
from typing import Callable, Any, Optional, Tuple, Type
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
        """
        Initialize retry configuration
        
        Args:
            max_attempts: Maximum number of retry attempts
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff calculation
            jitter: Whether to add random jitter to delays
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


async def retry_async(
    func: Callable,
    config: Optional[RetryConfig] = None,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[int, Exception, float], Any]] = None
) -> Any:
    """
    Retry an async function with exponential backoff
    
    Args:
        func: Async function to retry
        config: Retry configuration (uses defaults if None)
        exceptions: Tuple of exception types to catch and retry
        on_retry: Optional async callback called on each retry (attempt, error, delay)
    
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
                delay *= (0.5 + random.random() * 0.5)
            
            # Call retry callback if provided
            if on_retry:
                try:
                    if asyncio.iscoroutinefunction(on_retry):
                        await on_retry(attempt, e, delay)
                    else:
                        on_retry(attempt, e, delay)
                except Exception:
                    pass  # Don't let callback errors interrupt retry
            
            # Default logging if no callback provided
            else:
                print(f"   ⟳ Retry {attempt}/{config.max_attempts} after {delay:.1f}s: {str(e)}")
            
            # Wait before retry
            await asyncio.sleep(delay)
    
    # Should never reach here, but just in case
    if last_exception:
        raise last_exception
    raise RuntimeError("Retry logic failed unexpectedly")


def with_retry(
    config: Optional[RetryConfig] = None,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator to add retry logic to async functions
    
    Args:
        config: Retry configuration
        exceptions: Tuple of exception types to retry on
    
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


# Mixin for adding retry capability to clients

class RetryMixin:
    """
    Mixin to add retry capability to MCP clients
    
    Usage:
        class StdioMCPClient(RetryMixin, BaseMCPClient):
            def __init__(self, server_name: str, config: Dict[str, Any]):
                super().__init__(server_name, config)
                # retry_config is now available
    """
    
    def __init__(self, *args, retry_config: Optional[RetryConfig] = None, **kwargs):
        """
        Initialize retry mixin
        
        Args:
            retry_config: Optional retry configuration. If None, uses defaults.
        """
        super().__init__(*args, **kwargs)
        
        # Extract retry settings from config if available
        if hasattr(self, 'config') and isinstance(self.config, dict):
            retry_config = retry_config or RetryConfig(
                max_attempts=self.config.get("retry_attempts", 3),
                base_delay=self.config.get("retry_delay", 1.0),
                max_delay=self.config.get("retry_max_delay", 60.0)
            )
        
        self.retry_config = retry_config or RetryConfig()
    
    async def connect_with_retry(self) -> Any:
        """
        Connect with automatic retry on failure
        
        Returns:
            Result from connect() method
        """
        async def on_retry(attempt: int, error: Exception, delay: float):
            """Callback for retry attempts"""
            server_name = getattr(self, 'server_name', 'unknown')
            print(f"   ⟳ [{server_name}] Connection retry {attempt}/{self.retry_config.max_attempts}")
            print(f"      Error: {str(error)[:100]}")
            print(f"      Waiting {delay:.1f}s before retry...")
        
        # Retry on connection-related errors
        return await retry_async(
            func=self.connect,
            config=self.retry_config,
            exceptions=(
                ConnectionError,
                TimeoutError,
                OSError,
                RuntimeError,
                Exception  # Catch all for robustness
            ),
            on_retry=on_retry
        )


# Utility function to get retry config from dict

def get_retry_config_from_dict(config_dict: dict) -> RetryConfig:
    """
    Extract RetryConfig from configuration dictionary
    
    Args:
        config_dict: Configuration dictionary that may contain retry settings
    
    Returns:
        RetryConfig instance
    
    Example config:
        {
            "type": "stdio",
            "command": "npx",
            "args": ["..."],
            "retry_attempts": 5,
            "retry_delay": 2.0,
            "retry_max_delay": 120.0,
            "retry_jitter": true
        }
    """
    return RetryConfig(
        max_attempts=config_dict.get("retry_attempts", 3),
        base_delay=config_dict.get("retry_delay", 1.0),
        max_delay=config_dict.get("retry_max_delay", 60.0),
        exponential_base=config_dict.get("retry_exponential_base", 2.0),
        jitter=config_dict.get("retry_jitter", True)
    )


# Example enhanced client implementation

"""
# Example: Update stdio_client.py to use RetryMixin

from .retry import RetryMixin, get_retry_config_from_dict

class StdioMCPClient(RetryMixin, BaseMCPClient):
    '''MCP client using stdio connection with retry support'''
    
    def __init__(self, server_name: str, config: Dict[str, Any]):
        # RetryMixin will extract retry config from config dict
        super().__init__(server_name, config)
        self._client_context = None
        self._session_context = None
        self._read = None
        self._write = None
    
    async def connect(self) -> List[StructuredTool]:
        '''Connect to MCP server via stdio'''
        # ... existing connection logic ...
        pass


# Example: Update tool_factory.py to use retry

async def _load_mcp_server(self, server_name: str):
    '''Load external MCP server with retry support'''
    try:
        # Create client
        client = create_mcp_client(server_name, config)
        
        # Use retry logic if available
        if hasattr(client, 'connect_with_retry'):
            print(f"   ⟳ Connecting with retry support...")
            tools = await client.connect_with_retry()
        else:
            tools = await client.connect()
        
        self.mcp_clients[server_name] = client
        return tools
        
    except Exception as e:
        print(f"   ✗ Connection failed after all retries: {e}")
        return await self._fallback_to_custom(server_name)
"""