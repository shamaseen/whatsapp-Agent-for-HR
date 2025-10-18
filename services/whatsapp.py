import requests
from config import settings
from typing import Optional

class ChatwootClient:
    """Client for sending messages to Chatwoot"""

    def __init__(self):
        self.enabled = bool(settings.CHATWOOT_API_URL and settings.CHATWOOT_API_KEY)
        if self.enabled:
            self.base_url = settings.CHATWOOT_API_URL.rstrip('/')
            self.api_key = settings.CHATWOOT_API_KEY

    def send_message_to_chatwoot(self, account_id: int, conversation_id: int, message: str):
        """Send a message to a Chatwoot conversation"""
        if not self.enabled:
            raise ValueError("Chatwoot API not configured. Set CHATWOOT_API_URL and CHATWOOT_API_KEY in .env")

        url = f"{self.base_url}/api/v1/accounts/{account_id}/conversations/{conversation_id}/messages"
        headers = {
            "api_access_token": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "content": message,
            "message_type": "outgoing",
            "private": False
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()


class EvolutionAPIClient:
    """Evolution API client for direct WhatsApp integration"""

    def __init__(self):
        self.enabled = bool(settings.EVOLUTION_API_URL and settings.EVOLUTION_API_KEY)
        if self.enabled:
            self.base_url = settings.EVOLUTION_API_URL
            self.api_key = settings.EVOLUTION_API_KEY
            self.instance = settings.EVOLUTION_INSTANCE_NAME

    def send_message(self, remote_jid: str, text: str):
        """Send a text message via Evolution API"""
        if not self.enabled:
            raise ValueError("Evolution API not configured. Set EVOLUTION_API_URL, EVOLUTION_API_KEY, and EVOLUTION_INSTANCE_NAME in .env")

        url = f"{self.base_url}/message/sendText/{self.instance}"
        headers = {"apikey": self.api_key, "Content-Type": "application/json"}
        payload = {"number": remote_jid, "text": text}
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()


class MessagingClient:
    """Unified messaging client that supports both Chatwoot and Evolution API"""

    def __init__(self):
        self.chatwoot = ChatwootClient()
        self.evolution = EvolutionAPIClient()

    def send_message_to_chatwoot(self, account_id: int, conversation_id: int, message: str):
        """Send message via Chatwoot API"""
        return self.chatwoot.send_message_to_chatwoot(account_id, conversation_id, message)

    def send_message(self, remote_jid: str, text: str):
        """Send message via Evolution API"""
        return self.evolution.send_message(remote_jid, text)

    def is_chatwoot_enabled(self) -> bool:
        """Check if Chatwoot is configured"""
        return self.chatwoot.enabled

    def is_evolution_enabled(self) -> bool:
        """Check if Evolution API is configured"""
        return self.evolution.enabled


# Initialize unified client
messaging_client = MessagingClient()

# Backward compatibility aliases
evolution_client = messaging_client
chatwoot_client = messaging_client
