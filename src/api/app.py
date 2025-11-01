"""
FastAPI application factory
"""
import asyncio
from fastapi import FastAPI
from src.config import settings
from src.integrations.messaging import messaging_client


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="WhatsApp HR Assistant",
        version="1.0.0",
        description="AI-powered HR recruitment assistant with LangGraph"
    )

    # Register startup event
    @app.on_event("startup")
    async def startup_tasks():
        """Initialize application components and suppress MCP cleanup warnings"""

        # Set up asyncio exception handler to suppress harmless MCP cleanup warnings
        def handle_exception(loop, context):
            exception = context.get('exception')
            message = context.get('message', '')

            # Suppress known harmless MCP cleanup errors
            if exception:
                if isinstance(exception, (RuntimeError, GeneratorExit)):
                    if 'cancel scope' in str(exception):
                        return
            if 'async_generator' in message or 'cancel scope' in message:
                return

        try:
            loop = asyncio.get_event_loop()
            loop.set_exception_handler(handle_exception)
        except RuntimeError:
            pass

        # Validate messaging service configuration
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

    # Register routes
    from src.api.routes import webhook, dashboard, oauth, health
    app.include_router(webhook.router)
    app.include_router(dashboard.router)
    app.include_router(oauth.router)
    app.include_router(health.router)

    return app
