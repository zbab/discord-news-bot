"""
Client pour interagir avec l'API Dust via curl
"""
import subprocess
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DustClient:
    """Client pour l'API Dust utilisant curl"""

    BASE_URL = "https://dust.tt/api/v1"
    CURL_PATH = "/usr/bin/curl"

    def __init__(self, workspace_id: str, api_key: str):
        self.workspace_id = workspace_id
        self.api_key = api_key

    def _curl_get(self, url: str) -> Optional[dict]:
        """Exécute une requête GET via curl"""
        cmd = [
            self.CURL_PATH, "-s",
            "-H", f"Authorization: Bearer {self.api_key}",
            "-H", "Content-Type: application/json",
            url
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.error(f"Curl GET failed: {result.stderr}")
                return None
        except Exception as e:
            logger.error(f"Exception curl GET: {e}")
            return None

    def _curl_post(self, url: str, data: dict) -> Optional[dict]:
        """Exécute une requête POST via curl"""
        cmd = [
            self.CURL_PATH, "-s",
            "-X", "POST",
            "-H", f"Authorization: Bearer {self.api_key}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(data),
            url
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            response = json.loads(result.stdout) if result.stdout else {}

            # Vérifier si erreur dans la réponse
            if "error" in response:
                logger.error(f"API error: {response['error']}")
                return None

            return response
        except Exception as e:
            logger.error(f"Exception curl POST: {e}")
            return None

    async def post_message_to_conversation(self, conversation_id: str, message: str, agent_id: str = None) -> bool:
        """Envoie un message dans une conversation existante"""
        url = f"{self.BASE_URL}/w/{self.workspace_id}/assistant/conversations/{conversation_id}/messages"

        mentions = [{"configurationId": agent_id}] if agent_id else []

        payload = {
            "content": message,
            "mentions": mentions,
            "context": {
                "timezone": "Europe/Paris",
                "username": "Discord Bot",
                "email": None,
                "profilePictureUrl": None
            }
        }

        result = self._curl_post(url, payload)
        if result:
            logger.info("Message envoyé avec succès à la conversation")
            return True
        return False

    async def get_conversation(self, conversation_id: str) -> Optional[str]:
        """Récupère le dernier message de l'agent dans une conversation"""
        url = f"{self.BASE_URL}/w/{self.workspace_id}/assistant/conversations/{conversation_id}"

        data = self._curl_get(url)
        if not data:
            return None

        # Extraire le dernier message de l'agent
        conversation = data.get("conversation", {})
        content = conversation.get("content", [])

        agent_messages = []
        for item in content:
            if isinstance(item, list) and len(item) > 0:
                message = item[0]
                if isinstance(message, dict) and message.get("type") == "agent_message":
                    msg_content = message.get("content", "")
                    if msg_content:
                        agent_messages.append(msg_content)

        if agent_messages:
            logger.info(f"Trouvé {len(agent_messages)} message(s) d'agent")
            return agent_messages[-1]
        else:
            logger.warning("Aucun message d'agent trouvé")
            return None

    async def trigger_daily_summary(self, conversation_id: str, agent_id: str) -> bool:
        """Déclenche la génération du résumé quotidien"""
        # Mention dans le texte ET dans le payload pour déclencher l'agent
        message = f":mention[Actualité-réseaux]{{sId={agent_id}}} Peux-tu me donner un résumé des actualités importantes des réseaux sociaux d'aujourd'hui ?"
        success = await self.post_message_to_conversation(conversation_id, message, agent_id)
        if success:
            logger.info("Génération du résumé déclenchée avec succès")
        return success

    async def fetch_last_agent_message(self, conversation_id: str) -> Optional[str]:
        """Récupère uniquement le dernier message de l'agent"""
        return await self.get_conversation(conversation_id)
