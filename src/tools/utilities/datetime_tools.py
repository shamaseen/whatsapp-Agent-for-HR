from datetime import datetime
from langchain_core.tools import tool

@tool
def get_current_datetime() -> str:
    """Get the current date and time"""
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S %Z")
