"""
WhatsApp webhook endpoint
"""
from fastapi import APIRouter, Request, BackgroundTasks
from src.api.handlers.message_handler import process_message_background


router = APIRouter(tags=["webhook"])


@router.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """Main webhook for WhatsApp messages from Chatwoot - Returns immediately"""
    data = await request.json()
    body = data.get('body', data)

    if body.get('message_type') != 'incoming':
        return {"status": "ignored", "reason": "not incoming"}

    conversation = body.get('conversation', {})
    if 'hr' not in conversation.get('labels', []):
        return {"status": "ignored", "reason": "no hr label"}

    sender = conversation.get('meta', {}).get('sender', {})
    sender_phone = sender.get('phone_number', '').replace('+', '').replace(' ', '')

    # Ensure we have a valid phone number
    if not sender_phone:
        print("⚠️  No phone number found in webhook")
        return {"status": "ignored", "reason": "no phone number"}

    message_content = body.get('content', '')
    if not message_content:
        return {"status": "ignored", "reason": "no message content"}

    # Process message in background
    background_tasks.add_task(
        process_message_background,
        body=body,
        conversation=conversation,
        sender_identifier=sender.get('identifier'),
        sender_phone=sender_phone,
        message_content=message_content
    )

    print(f"📨 Webhook received from {sender_phone}, processing in background...")
    return {"status": "accepted", "message": "Processing in background"}
