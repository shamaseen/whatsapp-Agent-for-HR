"""
Request Logging Models
Tracks all incoming requests and AI agent behavior
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

Base = declarative_base()


class RequestLog(Base):
    """Log every incoming request and AI processing"""
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Request metadata
    request_id = Column(String(255), unique=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    sender_phone = Column(String(50), index=True)
    sender_identifier = Column(String(255), index=True)
    sender_name = Column(String(255))

    # Message content
    user_message = Column(Text)
    ai_response = Column(Text)

    # Processing details
    processing_time_ms = Column(Float)  # Total processing time
    llm_calls_count = Column(Integer, default=0)
    tools_used = Column(JSON)  # List of tools used

    # Status
    status = Column(String(50), index=True)  # success, error, pending
    error_message = Column(Text, nullable=True)

    # Conversation context
    conversation_id = Column(String(255), index=True)  # Chatwoot conversation ID
    had_history = Column(Boolean, default=False)
    history_count = Column(Integer, default=0)

    # Source
    source = Column(String(50), default='whatsapp')  # whatsapp, chatwoot, api


class ToolExecutionLog(Base):
    """Detailed log of each tool execution within a request"""
    __tablename__ = "tool_execution_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String(255), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Tool details
    tool_name = Column(String(100), index=True)
    tool_parameters = Column(JSON)
    tool_result = Column(Text)

    # Execution metrics
    execution_time_ms = Column(Float)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)

    # Sequence
    execution_order = Column(Integer)  # Order in which tool was called


class AIThinkingLog(Base):
    """Log AI reasoning and decision-making process"""
    __tablename__ = "ai_thinking_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String(255), index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Thinking details
    step_number = Column(Integer)
    thinking_content = Column(Text)
    decision_made = Column(String(255))

    # Context
    message_context = Column(Text)


# Create tables
engine = create_engine(settings.DATABASE_URL)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
