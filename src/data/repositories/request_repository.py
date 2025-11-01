"""
Request Logger Service
Provides comprehensive logging for all AI requests and tool executions
"""

import uuid
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from src.data.models.request_logs import RequestLog, ToolExecutionLog, AIThinkingLog, SessionLocal


class RequestLogger:
    """Logger for tracking all AI requests and executions"""

    def __init__(self):
        self.db = SessionLocal()

    def start_request(
        self,
        sender_phone: str,
        sender_identifier: str,
        user_message: str,
        sender_name: str = None,
        conversation_id: str = None,
        source: str = "whatsapp"
    ) -> str:
        """
        Start logging a new request
        Returns request_id for tracking
        """
        request_id = f"req_{uuid.uuid4().hex[:16]}"

        log = RequestLog(
            request_id=request_id,
            sender_phone=sender_phone,
            sender_identifier=sender_identifier,
            sender_name=sender_name,
            user_message=user_message,
            conversation_id=conversation_id,
            source=source,
            status="processing",
            timestamp=datetime.utcnow()
        )

        self.db.add(log)
        self.db.commit()

        return request_id

    def log_tool_execution(
        self,
        request_id: str,
        tool_name: str,
        parameters: Dict,
        result: Any,
        execution_time_ms: float,
        execution_order: int,
        success: bool = True,
        error: str = None
    ):
        """Log a tool execution within a request"""
        tool_log = ToolExecutionLog(
            request_id=request_id,
            tool_name=tool_name,
            tool_parameters=parameters,
            tool_result=str(result)[:5000],  # Limit result size
            execution_time_ms=execution_time_ms,
            execution_order=execution_order,
            success=success,
            error_message=error,
            timestamp=datetime.utcnow()
        )

        self.db.add(tool_log)
        self.db.commit()

    def log_ai_thinking(
        self,
        request_id: str,
        step_number: int,
        thinking_content: str,
        decision_made: str = None,
        context: str = None
    ):
        """Log AI reasoning/thinking process"""
        thinking_log = AIThinkingLog(
            request_id=request_id,
            step_number=step_number,
            thinking_content=thinking_content,
            decision_made=decision_made,
            message_context=context,
            timestamp=datetime.utcnow()
        )

        self.db.add(thinking_log)
        self.db.commit()

    def complete_request(
        self,
        request_id: str,
        ai_response: str,
        processing_time_ms: float,
        llm_calls_count: int,
        tools_used: List[str],
        had_history: bool = False,
        history_count: int = 0,
        status: str = "success",
        error: str = None
    ):
        """Complete a request log with final details"""
        log = self.db.query(RequestLog).filter_by(request_id=request_id).first()

        if log:
            log.ai_response = ai_response
            log.processing_time_ms = processing_time_ms
            log.llm_calls_count = llm_calls_count
            log.tools_used = tools_used
            log.had_history = had_history
            log.history_count = history_count
            log.status = status
            log.error_message = error

            self.db.commit()

    def get_recent_requests(self, limit: int = 50) -> List[Dict]:
        """Get recent requests with summary"""
        logs = self.db.query(RequestLog).order_by(
            RequestLog.timestamp.desc()
        ).limit(limit).all()

        return [
            {
                "request_id": log.request_id,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "sender_phone": log.sender_phone,
                "sender_name": log.sender_name,
                "user_message": log.user_message[:100] + "..." if len(log.user_message or "") > 100 else log.user_message,
                "ai_response": log.ai_response[:100] + "..." if len(log.ai_response or "") > 100 else log.ai_response,
                "processing_time_ms": log.processing_time_ms,
                "tools_used": log.tools_used,
                "status": log.status,
                "source": log.source
            }
            for log in logs
        ]

    def get_request_details(self, request_id: str) -> Optional[Dict]:
        """Get full details of a specific request including tool executions"""
        log = self.db.query(RequestLog).filter_by(request_id=request_id).first()

        if not log:
            return None

        # Get tool executions
        tool_logs = self.db.query(ToolExecutionLog).filter_by(
            request_id=request_id
        ).order_by(ToolExecutionLog.execution_order).all()

        # Get AI thinking logs
        thinking_logs = self.db.query(AIThinkingLog).filter_by(
            request_id=request_id
        ).order_by(AIThinkingLog.step_number).all()

        return {
            "request_id": log.request_id,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            "sender_phone": log.sender_phone,
            "sender_identifier": log.sender_identifier,
            "sender_name": log.sender_name,
            "user_message": log.user_message,
            "ai_response": log.ai_response,
            "processing_time_ms": log.processing_time_ms,
            "llm_calls_count": log.llm_calls_count,
            "tools_used": log.tools_used,
            "status": log.status,
            "error_message": log.error_message,
            "had_history": log.had_history,
            "history_count": log.history_count,
            "conversation_id": log.conversation_id,
            "source": log.source,
            "tool_executions": [
                {
                    "order": t.execution_order,
                    "tool_name": t.tool_name,
                    "parameters": t.tool_parameters,
                    "result": t.tool_result,
                    "execution_time_ms": t.execution_time_ms,
                    "success": t.success,
                    "error": t.error_message
                }
                for t in tool_logs
            ],
            "ai_thinking": [
                {
                    "step": t.step_number,
                    "thinking": t.thinking_content,
                    "decision": t.decision_made,
                    "context": t.message_context
                }
                for t in thinking_logs
            ]
        }

    def get_statistics(self) -> Dict:
        """Get overall statistics"""
        total_requests = self.db.query(RequestLog).count()
        successful = self.db.query(RequestLog).filter_by(status="success").count()
        failed = self.db.query(RequestLog).filter_by(status="error").count()
        processing = self.db.query(RequestLog).filter_by(status="processing").count()

        # Average processing time
        from sqlalchemy import func
        avg_time = self.db.query(func.avg(RequestLog.processing_time_ms)).filter(
            RequestLog.processing_time_ms.isnot(None)
        ).scalar() or 0

        # Most used tools
        tool_logs = self.db.query(ToolExecutionLog.tool_name, func.count(ToolExecutionLog.id)).group_by(
            ToolExecutionLog.tool_name
        ).order_by(func.count(ToolExecutionLog.id).desc()).limit(10).all()

        return {
            "total_requests": total_requests,
            "successful": successful,
            "failed": failed,
            "processing": processing,
            "success_rate": round((successful / total_requests * 100) if total_requests > 0 else 0, 2),
            "average_processing_time_ms": round(avg_time, 2),
            "most_used_tools": [{"tool": name, "count": count} for name, count in tool_logs]
        }

    def search_requests(
        self,
        sender_phone: str = None,
        status: str = None,
        limit: int = 50
    ) -> List[Dict]:
        """Search requests by criteria"""
        query = self.db.query(RequestLog)

        if sender_phone:
            query = query.filter(RequestLog.sender_phone.contains(sender_phone))
        if status:
            query = query.filter_by(status=status)

        logs = query.order_by(RequestLog.timestamp.desc()).limit(limit).all()

        return [
            {
                "request_id": log.request_id,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "sender_phone": log.sender_phone,
                "user_message": log.user_message[:100] + "..." if len(log.user_message or "") > 100 else log.user_message,
                "status": log.status,
                "processing_time_ms": log.processing_time_ms
            }
            for log in logs
        ]

    def close(self):
        """Close database session"""
        self.db.close()


# Global logger instance
request_logger = RequestLogger()
