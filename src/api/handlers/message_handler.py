"""
Message processing handler - Business logic for WhatsApp message processing
"""
import time
from langchain_core.messages import HumanMessage, AIMessage
from src.agents.complex_agent import create_complex_langgraph_agent
from src.agents.tool_factory import get_tools
from src.integrations.messaging import messaging_client
from src.data.repositories.request_repository import request_logger
from src.config import settings


# Initialize agent once at module level
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model=settings.MODEL_NAME,
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=settings.TEMPERATURE
)

tools = get_tools()

agent_app = create_complex_langgraph_agent(
    llm=llm,
    tools=tools,
    memory_type="postgres"
)


def process_message_background(
    body: dict,
    conversation: dict,
    sender_identifier: str,
    sender_phone: str,
    message_content: str
):
    """Background task to process message and send response"""
    start_time = time.time()
    request_id = None

    try:
        # Start request logging
        conversation_id = conversation.get('id')
        sender_name = conversation.get('meta', {}).get('sender', {}).get('name', 'Unknown')

        request_id = request_logger.start_request(
            sender_phone=sender_phone,
            sender_identifier=sender_identifier,
            user_message=message_content,
            sender_name=sender_name,
            conversation_id=str(conversation_id) if conversation_id else None,
            source="whatsapp"
        )

        # Build message for agent
        user_input = f"sender: {sender_phone}\n\nmessage: {message_content}"
        agent_messages = [HumanMessage(content=user_input)]

        # Run agent with checkpointer (memory managed automatically by thread_id)
        thread_id = sender_phone
        print(f"🤖 Processing message from {sender_phone}... [Request ID: {request_id}]")
        print(f"   Thread ID: {thread_id}")

        result = agent_app.invoke(
            input_text=user_input,
            thread_id=thread_id
        )

        print(f"   Message count in result: {len(result['messages'])}")

        # Debug: Check checkpoint was saved
        try:
            import psycopg
            conn = psycopg.connect(settings.DATABASE_URL)
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM checkpoints WHERE thread_id = %s", (thread_id,))
                count = cur.fetchone()[0]
                print(f"   Checkpoints in DB for {thread_id}: {count}")
            conn.close()
        except Exception as e:
            print(f"   ⚠️ Could not verify checkpoint: {e}")

        # Extract response and metadata from complex agent result
        last_ai_message = result.get("output", "I apologize, I couldn't process your request.")
        messages = result.get("messages", [])
        iterations = result.get("iterations", 0)

        # Extract tools used and count LLM calls
        tools_used = []
        llm_calls = iterations
        tool_order = 0

        for msg in messages:
            if isinstance(msg, AIMessage):
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tc in msg.tool_calls:
                        tool_name = tc.get('name', 'unknown')
                        tools_used.append(tool_name)

                        # Log individual tool execution
                        tool_order += 1
                        request_logger.log_tool_execution(
                            request_id=request_id,
                            tool_name=tool_name,
                            parameters=tc.get('args', {}),
                            result="executed",
                            execution_time_ms=0,
                            execution_order=tool_order,
                            success=True
                        )

        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000

        # Complete request log
        request_logger.complete_request(
            request_id=request_id,
            ai_response=last_ai_message,
            processing_time_ms=processing_time,
            llm_calls_count=llm_calls,
            tools_used=tools_used,
            had_history=True,
            history_count=len(messages),
            status="success"
        )

        # Send response back to user
        conversation_id = conversation.get('id')
        account_id = body.get('account', {}).get('id')

        if conversation_id and account_id and messaging_client.is_chatwoot_enabled():
            # Chatwoot webhook - send via Chatwoot API
            messaging_client.send_message_to_chatwoot(
                account_id=account_id,
                conversation_id=conversation_id,
                message=last_ai_message
            )
            print(f"✅ Response sent via Chatwoot to conversation {conversation_id}")

        elif messaging_client.is_evolution_enabled():
            # Fallback to Evolution API (direct WhatsApp)
            messaging_client.send_message(sender_identifier, last_ai_message)
            print(f"✅ Response sent via Evolution API to {sender_identifier}")

        else:
            print(f"⚠️  No messaging service configured. Response not sent.")
            print(f"   Would have sent: {last_ai_message[:100]}...")

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error in background task: {error_msg}")
        import traceback
        traceback.print_exc()

        # Log error
        if request_id:
            processing_time = (time.time() - start_time) * 1000
            request_logger.complete_request(
                request_id=request_id,
                ai_response="Error occurred",
                processing_time_ms=processing_time,
                llm_calls_count=0,
                tools_used=[],
                status="error",
                error=error_msg
            )
