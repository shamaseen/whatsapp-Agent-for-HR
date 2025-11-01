# Utils module
# jupyter_helper is optional and not required for core functionality

try:
    from .jupyter_helper import suppress_mcp_cleanup_warnings, setup_jupyter_environment
    __all__ = ['suppress_mcp_cleanup_warnings', 'setup_jupyter_environment']
except ImportError:
    # jupyter_helper not available, skip
    __all__ = []
