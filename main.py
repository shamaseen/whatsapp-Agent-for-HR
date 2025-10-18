"""
WhatsApp HR Assistant - Main Application
FastAPI server with LangGraph agent for HR recruitment tasks
"""

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage
from agents.hr_agent import create_agent
from services.whatsapp import messaging_client
from services.memory import ConversationMemory
from services.request_logger import request_logger
from config import settings
import time

app = FastAPI(title="WhatsApp HR Assistant", version="1.0.0")
agent_app = create_agent()

# Validate configuration on startup
@app.on_event("startup")
async def validate_config():
    """Validate that at least one messaging service is configured"""
    if not messaging_client.is_chatwoot_enabled() and not messaging_client.is_evolution_enabled():
        print("⚠️  WARNING: Neither Chatwoot nor Evolution API is configured!")
        print("    Please configure at least one messaging service in .env")
        print("    - For Chatwoot: CHATWOOT_API_URL and CHATWOOT_API_KEY")
        print("    - For Evolution API: EVOLUTION_API_URL, EVOLUTION_API_KEY, EVOLUTION_INSTANCE_NAME")
    else:
        if messaging_client.is_chatwoot_enabled():
            print("✅ Chatwoot API configured")
        if messaging_client.is_evolution_enabled():
            print("✅ Evolution API configured")

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

        # Initialize memory
        memory = ConversationMemory(sender_identifier)
        history = memory.get_history(limit=2)

        # Build messages for agent
        agent_messages = []
        for h in history:
            if h['role'] == 'user':
                agent_messages.append(HumanMessage(content=h['content']))
            elif h['role'] == 'assistant':
                agent_messages.append(AIMessage(content=h['content']))

        # Add current message
        user_input = f"sender: {sender_phone}\n\nmessage: {message_content}"
        agent_messages.append(HumanMessage(content=user_input))

        # Run agent
        print(f"🤖 Processing message from {sender_phone}... [Request ID: {request_id}]")
        result = agent_app.invoke({
            "messages": agent_messages,
            "sender_phone": sender_phone,
            "sender_identifier": sender_identifier
        })

        # Extract tools used and count LLM calls
        tools_used = []
        llm_calls = 0
        tool_order = 0

        for msg in result["messages"]:
            if isinstance(msg, AIMessage):
                llm_calls += 1
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
                            execution_time_ms=0,  # Would need timing per tool
                            execution_order=tool_order,
                            success=True
                        )

        # Get response
        final_messages = result["messages"]
        last_ai_message = None
        for msg in reversed(final_messages):
            if isinstance(msg, AIMessage) and msg.content:
                last_ai_message = msg.content
                break

        if not last_ai_message:
            last_ai_message = "I apologize, I couldn't process your request."

        # Save to memory
        memory.add_message("user", message_content)
        memory.add_message("assistant", last_ai_message)

        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # Convert to ms

        # Complete request log
        request_logger.complete_request(
            request_id=request_id,
            ai_response=last_ai_message,
            processing_time_ms=processing_time,
            llm_calls_count=llm_calls,
            tools_used=tools_used,
            had_history=len(history) > 0,
            history_count=len(history),
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


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """Main webhook for WhatsApp messages from Chatwoot - Returns immediately"""
    data = await request.json()

    # Extract body from webhook (Chatwoot format)
    body = data.get('body', data)

    # Filter messages
    message_type = body.get('message_type')
    if message_type != 'incoming':
        return {"status": "ignored", "reason": "not incoming"}

    # Get conversation data
    conversation = body.get('conversation', {})
    labels = conversation.get('labels', [])
    if 'hr' not in labels:
        return {"status": "ignored", "reason": "no hr label"}

    # Get sender information from conversation meta
    sender = conversation.get('meta', {}).get('sender', {})
    sender_identifier = sender.get('identifier')
    sender_phone = sender.get('phone_number', '').replace('+', '').replace(' ', '')
    sender_name = sender.get('name', 'Unknown')

    # Get message content
    message_content = body.get('content', '')

    if not message_content:
        return {"status": "ignored", "reason": "no message content"}

    # Add background task to process and send response
    background_tasks.add_task(
        process_message_background,
        body=body,
        conversation=conversation,
        sender_identifier=sender_identifier,
        sender_phone=sender_phone,
        message_content=message_content
    )

    # Return immediately
    print(f"📨 Webhook received from {sender_phone}, processing in background...")
    return {"status": "accepted", "message": "Processing in background"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Main dashboard HTML page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>WhatsApp HR Assistant - Dashboard</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1400px;
                margin: 0 auto;
            }
            .header {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
            .header h1 {
                color: #667eea;
                margin-bottom: 10px;
            }
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            .stat-card {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
            }
            .stat-card h3 {
                font-size: 2em;
                color: #667eea;
                margin-bottom: 10px;
            }
            .stat-card p {
                color: #666;
                font-size: 0.9em;
            }
            .requests-section {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .requests-section h2 {
                margin-bottom: 20px;
                color: #667eea;
            }
            .filters {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }
            .filters input, .filters select, .filters button {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
            }
            .filters button {
                background: #667eea;
                color: white;
                cursor: pointer;
                border: none;
            }
            .filters button:hover {
                background: #5568d3;
            }
            .request-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            .request-table th {
                background: #f7f7f7;
                padding: 15px;
                text-align: left;
                font-weight: 600;
                border-bottom: 2px solid #ddd;
            }
            .request-table td {
                padding: 15px;
                border-bottom: 1px solid #eee;
            }
            .request-table tr:hover {
                background: #f9f9f9;
            }
            .status-badge {
                padding: 5px 10px;
                border-radius: 20px;
                font-size: 0.8em;
                font-weight: 600;
            }
            .status-success {
                background: #d4edda;
                color: #155724;
            }
            .status-error {
                background: #f8d7da;
                color: #721c24;
            }
            .status-processing {
                background: #fff3cd;
                color: #856404;
            }
            .view-details {
                color: #667eea;
                text-decoration: none;
                font-weight: 600;
                cursor: pointer;
            }
            .view-details:hover {
                text-decoration: underline;
            }
            .modal {
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                overflow-y: auto;
            }
            .modal-content {
                background: white;
                margin: 50px auto;
                padding: 30px;
                border-radius: 10px;
                max-width: 900px;
                max-height: 80vh;
                overflow-y: auto;
            }
            .close {
                float: right;
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
                color: #aaa;
            }
            .close:hover {
                color: #000;
            }
            .detail-section {
                margin: 20px 0;
                padding: 15px;
                background: #f9f9f9;
                border-radius: 5px;
            }
            .detail-section h3 {
                color: #667eea;
                margin-bottom: 10px;
            }
            .tool-execution {
                background: white;
                padding: 10px;
                margin: 10px 0;
                border-left: 3px solid #667eea;
            }
            .refresh-btn {
                position: fixed;
                bottom: 30px;
                right: 30px;
                background: #667eea;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 50px;
                cursor: pointer;
                box-shadow: 0 4px 6px rgba(0,0,0,0.2);
                font-weight: 600;
            }
            .refresh-btn:hover {
                background: #5568d3;
            }
            .loading {
                text-align: center;
                padding: 40px;
                color: #999;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 WhatsApp HR Assistant Dashboard</h1>
                <p>Real-time monitoring and logging of AI agent requests</p>
            </div>

            <div class="stats-grid" id="stats">
                <div class="stat-card">
                    <h3>—</h3>
                    <p>Total Requests</p>
                </div>
                <div class="stat-card">
                    <h3>—</h3>
                    <p>Success Rate</p>
                </div>
                <div class="stat-card">
                    <h3>—</h3>
                    <p>Avg Processing Time</p>
                </div>
                <div class="stat-card">
                    <h3>—</h3>
                    <p>Failed Requests</p>
                </div>
            </div>

            <div class="requests-section">
                <h2>Recent Requests</h2>
                <div class="filters">
                    <input type="text" id="phoneFilter" placeholder="Filter by phone...">
                    <select id="statusFilter">
                        <option value="">All Status</option>
                        <option value="success">Success</option>
                        <option value="error">Error</option>
                        <option value="processing">Processing</option>
                    </select>
                    <button onclick="applyFilters()">Apply Filters</button>
                    <button onclick="clearFilters()">Clear</button>
                </div>

                <div id="requestsList">
                    <div class="loading">Loading requests...</div>
                </div>
            </div>
        </div>

        <button class="refresh-btn" onclick="loadData()">🔄 Refresh</button>

        <!-- Modal for request details -->
        <div id="detailsModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal()">&times;</span>
                <div id="modalContent">Loading...</div>
            </div>
        </div>

        <script>
            let allRequests = [];

            async function loadStatistics() {
                try {
                    const response = await fetch('/api/dashboard/stats');
                    const stats = await response.json();

                    const statsHTML = `
                        <div class="stat-card">
                            <h3>${stats.total_requests}</h3>
                            <p>Total Requests</p>
                        </div>
                        <div class="stat-card">
                            <h3>${stats.success_rate}%</h3>
                            <p>Success Rate</p>
                        </div>
                        <div class="stat-card">
                            <h3>${Math.round(stats.average_processing_time_ms)}ms</h3>
                            <p>Avg Processing Time</p>
                        </div>
                        <div class="stat-card">
                            <h3>${stats.failed}</h3>
                            <p>Failed Requests</p>
                        </div>
                    `;

                    document.getElementById('stats').innerHTML = statsHTML;
                } catch (error) {
                    console.error('Error loading statistics:', error);
                }
            }

            async function loadRequests() {
                try {
                    const response = await fetch('/api/dashboard/requests?limit=50');
                    allRequests = await response.json();
                    displayRequests(allRequests);
                } catch (error) {
                    console.error('Error loading requests:', error);
                    document.getElementById('requestsList').innerHTML = '<div class="loading">Error loading requests</div>';
                }
            }

            function displayRequests(requests) {
                if (requests.length === 0) {
                    document.getElementById('requestsList').innerHTML = '<div class="loading">No requests found</div>';
                    return;
                }

                const tableHTML = `
                    <table class="request-table">
                        <thead>
                            <tr>
                                <th>Timestamp</th>
                                <th>Sender</th>
                                <th>Message</th>
                                <th>Status</th>
                                <th>Processing Time</th>
                                <th>Tools Used</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${requests.map(req => `
                                <tr>
                                    <td>${new Date(req.timestamp).toLocaleString()}</td>
                                    <td>
                                        <strong>${req.sender_name || 'Unknown'}</strong><br>
                                        <small>${req.sender_phone}</small>
                                    </td>
                                    <td>${req.user_message || 'N/A'}</td>
                                    <td>
                                        <span class="status-badge status-${req.status}">
                                            ${req.status}
                                        </span>
                                    </td>
                                    <td>${req.processing_time_ms ? Math.round(req.processing_time_ms) + 'ms' : 'N/A'}</td>
                                    <td>${req.tools_used ? req.tools_used.join(', ') : 'None'}</td>
                                    <td>
                                        <a class="view-details" onclick="viewDetails('${req.request_id}')">
                                            View Details
                                        </a>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                `;

                document.getElementById('requestsList').innerHTML = tableHTML;
            }

            async function viewDetails(requestId) {
                document.getElementById('detailsModal').style.display = 'block';
                document.getElementById('modalContent').innerHTML = '<div class="loading">Loading details...</div>';

                try {
                    const response = await fetch(`/api/dashboard/request/${requestId}`);
                    const details = await response.json();

                    const modalHTML = `
                        <h2>Request Details</h2>
                        <div class="detail-section">
                            <h3>Request Information</h3>
                            <p><strong>Request ID:</strong> ${details.request_id}</p>
                            <p><strong>Timestamp:</strong> ${new Date(details.timestamp).toLocaleString()}</p>
                            <p><strong>Sender:</strong> ${details.sender_name} (${details.sender_phone})</p>
                            <p><strong>Status:</strong> <span class="status-badge status-${details.status}">${details.status}</span></p>
                            <p><strong>Processing Time:</strong> ${Math.round(details.processing_time_ms || 0)}ms</p>
                            <p><strong>LLM Calls:</strong> ${details.llm_calls_count}</p>
                        </div>

                        <div class="detail-section">
                            <h3>User Message</h3>
                            <p>${details.user_message}</p>
                        </div>

                        <div class="detail-section">
                            <h3>AI Response</h3>
                            <p>${details.ai_response || 'No response yet'}</p>
                        </div>

                        ${details.tool_executions && details.tool_executions.length > 0 ? `
                            <div class="detail-section">
                                <h3>Tool Executions</h3>
                                ${details.tool_executions.map(tool => `
                                    <div class="tool-execution">
                                        <p><strong>Tool:</strong> ${tool.tool_name}</p>
                                        <p><strong>Parameters:</strong> ${JSON.stringify(tool.parameters)}</p>
                                        <p><strong>Success:</strong> ${tool.success ? '✅' : '❌'}</p>
                                        ${tool.error ? `<p><strong>Error:</strong> ${tool.error}</p>` : ''}
                                    </div>
                                `).join('')}
                            </div>
                        ` : ''}

                        ${details.error_message ? `
                            <div class="detail-section">
                                <h3>Error Details</h3>
                                <p style="color: red;">${details.error_message}</p>
                            </div>
                        ` : ''}
                    `;

                    document.getElementById('modalContent').innerHTML = modalHTML;
                } catch (error) {
                    console.error('Error loading details:', error);
                    document.getElementById('modalContent').innerHTML = '<div class="loading">Error loading details</div>';
                }
            }

            function closeModal() {
                document.getElementById('detailsModal').style.display = 'none';
            }

            function applyFilters() {
                const phoneFilter = document.getElementById('phoneFilter').value.toLowerCase();
                const statusFilter = document.getElementById('statusFilter').value;

                let filtered = allRequests;

                if (phoneFilter) {
                    filtered = filtered.filter(req =>
                        req.sender_phone.toLowerCase().includes(phoneFilter) ||
                        (req.sender_name && req.sender_name.toLowerCase().includes(phoneFilter))
                    );
                }

                if (statusFilter) {
                    filtered = filtered.filter(req => req.status === statusFilter);
                }

                displayRequests(filtered);
            }

            function clearFilters() {
                document.getElementById('phoneFilter').value = '';
                document.getElementById('statusFilter').value = '';
                displayRequests(allRequests);
            }

            function loadData() {
                loadStatistics();
                loadRequests();
            }

            // Load data on page load
            loadData();

            // Auto-refresh every 10 seconds
            setInterval(loadData, 10000);

            // Close modal when clicking outside
            window.onclick = function(event) {
                const modal = document.getElementById('detailsModal');
                if (event.target == modal) {
                    modal.style.display = 'none';
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    return request_logger.get_statistics()


@app.get("/api/dashboard/requests")
async def get_dashboard_requests(limit: int = 50):
    """Get recent requests"""
    return request_logger.get_recent_requests(limit=limit)


@app.get("/api/dashboard/request/{request_id}")
async def get_request_details(request_id: str):
    """Get detailed information about a specific request"""
    details = request_logger.get_request_details(request_id)
    if not details:
        return JSONResponse(
            status_code=404,
            content={"error": "Request not found"}
        )
    return details


@app.get("/api/dashboard/search")
async def search_requests(phone: str = None, status: str = None, limit: int = 50):
    """Search requests by criteria"""
    return request_logger.search_requests(
        sender_phone=phone,
        status=status,
        limit=limit
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
