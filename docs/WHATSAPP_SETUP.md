# WhatsApp Integration Setup Guide

Complete guide to setting up WhatsApp integration for the WhatsApp HR Assistant.

---

## Overview

The WhatsApp HR Assistant supports two WhatsApp integration methods:

1. **Chatwoot** (Recommended) - Professional WhatsApp Business solution
2. **Evolution API** - Direct WhatsApp API integration

---

## Option 1: Chatwoot Setup

### What is Chatwoot?

Chatwoot is an open-source customer engagement suite that provides WhatsApp Business integration through WhatsApp Cloud API.

### Step 1: Install Chatwoot

**Option A: Cloud Installation**
1. Visit [chatwoot.com](https://www.chatwoot.com)
2. Sign up for an account
3. Create a new workspace

**Option B: Self-Hosted**
```bash
# Docker installation
docker run -d --name chatwoot-app \
  -p 3000:3000 \
  -v /home/chatwoot/db:/home/chatwoot/db \
  chatwoot/chatwoot:latest
```

### Step 2: Enable WhatsApp Channel

1. **Go to Settings**
   - Login to Chatwoot dashboard
   - Navigate to "Settings" → "Inboxes"

2. **Create WhatsApp Channel**
   - Click "Add Inbox"
   - Choose "WhatsApp"
   - Click "Continue"

3. **Get Credentials**
   - Copy **API URL** (e.g., `https://app.chatwoot.com`)
   - Copy **API Token** (from your Chatwoot profile settings)

### Step 3: Configure Environment

```env
# Chatwoot Configuration
CHATWOOT_API_URL=https://your-chatwoot-domain.com
CHATWOOT_API_KEY=your_api_token_here
```

### Step 4: Connect Webhook

1. **Get Webhook URL**
   - Your Chatwoot URL: `https://your-chatwoot.com`
   - Webhook endpoint: `https://your-app.com/webhook/whatsapp`

2. **Configure in Chatwoot**
   - Settings → Inboxes → WhatsApp
   - Add webhook: `https://your-app.com/webhook/whatsapp`
   - Enable events: "message_created", "message_updated"

---

## Option 2: Evolution API Setup

### What is Evolution API?

Evolution API is a direct WhatsApp API integration that works with WhatsApp Web.

### Step 1: Install Evolution API

**Docker Installation:**
```bash
docker run -d \
  --name evolution-api \
  -p 8080:8080 \
  -p 8081:8081 \
  evolutionman/evolution-api:latest
```

### Step 2: Create Instance

```bash
# Create instance
curl -X POST http://localhost:8080/instance/create \
  -H "apikey: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "instanceName": "whatsapp-hr-assistant",
    "token": "your-instance-token",
    "number": "your-whatsapp-number"
  }'

# Get instance info
curl -X GET http://localhost:8080/instance/fetchInstances \
  -H "apikey: YOUR_API_KEY"
```

### Step 3: Configure Environment

```env
# Evolution API Configuration
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=your_api_key
EVOLUTION_INSTANCE_NAME=whatsapp-hr-assistant
```

### Step 4: Generate QR Code

```python
from src.integrations.whatsapp import evolution_client

# Connect WhatsApp
qr_code = evolution_client.get_qr_code()
print("Scan this QR code with WhatsApp:")
print(qr_code)
```

---

## Test Integration

### Test 1: Verify Connection

```python
from src.integrations.whatsapp import initialize_whatsapp

# Initialize WhatsApp integration
whatsapp = initialize_whatsapp()

if whatsapp:
    print("✅ WhatsApp integration ready!")
    print(f"Type: {whatsapp.type}")
else:
    print("❌ WhatsApp not configured")
```

### Test 2: Send Test Message

```python
# Send message via Chatwoot
from src.integrations.whatsapp import chatwoot_client

chatwoot_client.send_message(
    conversation_id="12345",
    message="Hello from WhatsApp HR Assistant!"
)

# OR send via Evolution API
from src.integrations.whatsapp import evolution_client

evolution_client.send_message(
    number="+1234567890",
    message="Hello from WhatsApp HR Assistant!"
)
```

---

## Webhook Configuration

### Chatwoot Webhook

**Webhook URL:**
```
https://your-domain.com/webhook/whatsapp
```

**Events to enable:**
- `message_created` - New messages
- `message_updated` - Message edits
- `conversation_resolved` - Conversation closed

**Headers:**
```
api_access_token: YOUR_API_TOKEN
```

### Evolution API Webhook

**Configure in Evolution API:**
```json
{
  "webhook": {
    "url": "https://your-domain.com/webhook/whatsapp",
    "events": ["messages.upsert", "messages.update"]
  }
}
```

---

## Environment Variables Reference

### Chatwoot

```env
CHATWOOT_API_URL=https://app.chatwoot.com
CHATWOOT_API_KEY=your_api_token
```

### Evolution API

```env
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=your_api_key
EVOLUTION_INSTANCE_NAME=your_instance_name
```

---

## Troubleshooting

### Error: `Connection refused`

**Cause**: Chatwoot/Evolution API not running or wrong URL.

**Solution**:
1. Verify service is running:
   ```bash
   # Chatwoot
   docker ps | grep chatwoot
   
   # Evolution API
   docker ps | grep evolution
   ```
2. Check URL in .env matches running service
3. Test connection:
   ```bash
   curl http://localhost:3000/api/v1/accounts  # Chatwoot
   curl http://localhost:8080/instance/fetchInstances  # Evolution
   ```

### Error: `Invalid API token`

**Cause**: Wrong or expired API token.

**Solution**:
1. Chatwoot: Get new token from Profile Settings
2. Evolution API: Regenerate instance token
3. Update .env with new token

### Error: `WhatsApp not connected`

**Cause**: WhatsApp not paired with instance.

**Solution**:
1. **For Evolution API**: Scan QR code
2. **For Chatwoot**: WhatsApp Business account not connected
   - Visit Chatwoot WhatsApp settings
   - Follow connection process

### Error: `Webhook not receiving messages`

**Cause**: Webhook URL not reachable or misconfigured.

**Solution**:
1. Test webhook URL:
   ```bash
   curl -X POST https://your-domain.com/webhook/whatsapp \
     -H "Content-Type: application/json" \
     -d '{"test": true}'
   ```
2. Check Chatwoot/Evolution API webhook configuration
3. Ensure SSL certificate is valid
4. Check firewall/security group rules

---

## Production Deployment

### Domain Configuration

1. **Get SSL certificate** (Let's Encrypt recommended)
2. **Configure DNS** to point your domain to the server
3. **Update webhook URLs** in Chatwoot/Evolution API to use HTTPS

### Security

1. **Verify webhook signatures** (if supported)
2. **Rate limiting** on webhook endpoint
3. **Authentication** for API calls
4. **Whitelist IPs** if possible

### Monitoring

1. **Set up health checks**
2. **Monitor message delivery**
3. **Track API errors**
4. **Alert on failures**

---

## Message Flow

### Incoming Messages

1. **User sends message** on WhatsApp
2. **Chatwoot/Evolution API** receives message
3. **Webhook** called: `POST /webhook/whatsapp`
4. **FastAPI handler** processes message
5. **Agent** generates response
6. **Response sent back** via Chatwoot/Evolution API
7. **User receives message** on WhatsApp

### Outgoing Messages

```python
# Send message
from src.integrations.whatsapp import send_whatsapp_message

send_whatsapp_message(
    to="+1234567890",
    message="Your interview is scheduled for tomorrow at 2pm",
    media_url=None  # Optional
)
```

---

## Supported Message Types

- Text messages ✅
- Images ✅
- Documents (PDF) ✅
- Audio messages ✅
- Video messages ✅
- Location ✅
- Contact cards ✅

---

## API Reference

### Chatwoot Client

```python
from src.integrations.whatsapp import chatwoot_client

# Send message
chatwoot_client.send_message(conversation_id, message)

# Get conversation
conversation = chatwoot_client.get_conversation(conversation_id)

# Mark as read
chatwoot_client.mark_as_read(conversation_id)
```

### Evolution API Client

```python
from src.integrations.whatsapp import evolution_client

# Send message
evolution_client.send_message(number, message)

# Send media
evolution_client.send_media(number, media_url, media_type)

# Get instance status
status = evolution_client.get_instance_status()
```

---

## See Also

- [Chatwoot Documentation](https://www.chatwoot.com/docs)
- [Evolution API Documentation](https://github.com/EvolutionAPI/evolution-api)
- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)

---

**Last Updated**: October 31, 2025
