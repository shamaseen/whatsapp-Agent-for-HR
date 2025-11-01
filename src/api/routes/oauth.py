"""
OAuth callback endpoints
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter(tags=["oauth"])


@router.get("/oauth/webex/callback")
async def webex_oauth_callback(code: str = None, error: str = None):
    """OAuth2 callback for Webex authorization"""
    if error:
        return HTMLResponse(
            f"<html><body><h1>Error</h1><p>Authorization failed: {error}</p></body></html>",
            status_code=400
        )

    if not code:
        return HTMLResponse(
            "<html><body><h1>Error</h1><p>No authorization code received</p></body></html>",
            status_code=400
        )

    try:
        from src.integrations.webex_sdk import webex_client

        if not webex_client:
            return HTMLResponse(
                "<html><body><h1>Error</h1><p>Webex client not initialized</p></body></html>",
                status_code=500
            )

        # Exchange code for token
        token_data = webex_client.exchange_code_for_token(code)

        return HTMLResponse(f"""
            <html>
            <body>
                <h1>Success!</h1>
                <p>Webex has been authorized successfully.</p>
                <p>Access token saved to .webex_token.json</p>
                <p>You can close this window and use the Webex integration.</p>
                <hr>
                <small>Token expires in: {token_data.get('expires_in', 'N/A')} seconds</small>
            </body>
            </html>
        """)

    except Exception as e:
        return HTMLResponse(
            f"<html><body><h1>Error</h1><p>Failed to exchange token: {str(e)}</p></body></html>",
            status_code=500
        )
