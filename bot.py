"""
Bot Discord pour envoyer les résumés quotidiens de Dust
"""
import asyncio
import logging
import os
from datetime import datetime, time, timedelta
from typing import Optional
import aiohttp
from dotenv import load_dotenv

from dust_client import DustClient

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

DUST_WORKSPACE_ID = os.getenv('DUST_WORKSPACE_ID')
DUST_API_KEY = os.getenv('DUST_API_KEY')
DUST_CONVERSATION_ID = os.getenv('DUST_CONVERSATION_ID')
DUST_AGENT_ID = os.getenv('DUST_AGENT_ID')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
DAILY_GENERATION_TIME = os.getenv('DAILY_GENERATION_TIME', '07:58')
DAILY_FETCH_TIME = os.getenv('DAILY_FETCH_TIME', '08:00')


class DailyNewsBot:
    """Bot pour envoyer les résumés quotidiens sur Discord"""

    def __init__(self):
        """Initialise le bot"""
        self.dust_client = DustClient(DUST_WORKSPACE_ID, DUST_API_KEY)
        self.webhook_url = DISCORD_WEBHOOK_URL
        self.conversation_id = DUST_CONVERSATION_ID
        self.agent_id = DUST_AGENT_ID
        self.generation_time = self._parse_time(DAILY_GENERATION_TIME)
        self.fetch_time = self._parse_time(DAILY_FETCH_TIME)
        self.running = False

    @staticmethod
    def _parse_time(time_str: str) -> time:
        """Parse une string de temps au format HH:MM"""
        hour, minute = map(int, time_str.split(':'))
        return time(hour=hour, minute=minute)

    async def send_discord_message(self, content: str) -> bool:
        """
        Envoie un message via webhook Discord (découpe si > 2000 caractères)

        Args:
            content: Contenu du message à envoyer

        Returns:
            True si succès, False sinon
        """
        try:
            # Discord limite à 2000 caractères par message
            messages = []
            if len(content) <= 1900:
                messages.append(content)
            else:
                # Découper le message
                remaining = content
                while remaining:
                    chunk = remaining[:1900]
                    remaining = remaining[1900:]
                    messages.append(chunk + ("..." if remaining else ""))

            async with aiohttp.ClientSession() as session:
                for i, msg in enumerate(messages):
                    payload = {
                        "content": msg,
                        "username": "Dust Daily News"
                    }
                    async with session.post(self.webhook_url, json=payload) as response:
                        if response.status not in (200, 204):
                            error_text = await response.text()
                            logger.error(f"Erreur lors de l'envoi du message Discord (partie {i+1}): {response.status} - {error_text}")
                            return False

            logger.info(f"Message envoyé avec succès sur Discord ({len(messages)} partie(s))")
            return True
        except Exception as e:
            logger.error(f"Exception lors de l'envoi du message Discord: {e}")
            return False

    async def trigger_generation(self):
        """Déclenche la génération du résumé par l'agent Dust"""
        logger.info(f"Déclenchement de la génération du résumé (conversation: {self.conversation_id}, agent: {self.agent_id})")

        success = await self.dust_client.trigger_daily_summary(self.conversation_id, self.agent_id)
        if success:
            logger.info("Génération déclenchée avec succès, l'agent est en train de générer le résumé...")
        else:
            logger.error("Échec du déclenchement de la génération")

        return success

    async def fetch_and_send_summary(self):
        """Récupère le dernier message de l'agent et l'envoie sur Discord"""
        logger.info(f"Récupération du dernier message de l'agent depuis la conversation {self.conversation_id}...")

        try:
            # Récupération du dernier message de l'agent
            summary = await self.dust_client.fetch_last_agent_message(self.conversation_id)

            if summary:
                logger.info(f"Résumé récupéré avec succès ({len(summary)} caractères)")

                # Formatage du message
                today = datetime.now().strftime('%d/%m/%Y')
                message = f"📰 **Résumé quotidien - {today}**\n\n{summary}"

                # Envoi sur Discord
                success = await self.send_discord_message(message)
                if success:
                    logger.info("Résumé quotidien envoyé avec succès")
                else:
                    logger.error("Échec de l'envoi du résumé sur Discord")
            else:
                logger.error("Impossible de récupérer le résumé depuis Dust")
                await self.send_discord_message(
                    "❌ Erreur: Impossible de récupérer le résumé quotidien depuis Dust."
                )
        except Exception as e:
            logger.error(f"Erreur lors de la récupération/envoi du résumé: {e}")
            await self.send_discord_message(
                f"❌ Erreur lors de la récupération du résumé: {str(e)}"
            )

    async def wait_until_time(self, target_time: time) -> datetime:
        """
        Attend jusqu'à l'heure cible

        Returns:
            La datetime à laquelle l'attente s'est terminée
        """
        now = datetime.now()
        target = datetime.combine(now.date(), target_time)

        # Si l'heure est déjà passée aujourd'hui, planifier pour demain
        if target <= now:
            target = target + timedelta(days=1)

        wait_seconds = (target - now).total_seconds()
        logger.info(f"Attente jusqu'à {target.strftime('%Y-%m-%d %H:%M:%S')} ({wait_seconds:.0f} secondes)")
        await asyncio.sleep(wait_seconds)
        return target

    async def run(self):
        """Lance le bot en mode continu"""
        self.running = True
        logger.info(f"Bot démarré")
        logger.info(f"  - Génération programmée à: {self.generation_time.strftime('%H:%M')}")
        logger.info(f"  - Récupération programmée à: {self.fetch_time.strftime('%H:%M')}")

        # Message de démarrage
        await self.send_discord_message(
            f"✅ Bot de résumé quotidien démarré\n"
            f"Conversation Dust: `{self.conversation_id}`\n"
            f"Agent: `{self.agent_id}`\n"
            f"Génération à: **{self.generation_time.strftime('%H:%M')}**\n"
            f"Envoi à: **{self.fetch_time.strftime('%H:%M')}**"
        )

        while self.running:
            try:
                # Étape 1: Attendre l'heure de génération (7h58)
                logger.info("=== Attente de l'heure de génération ===")
                await self.wait_until_time(self.generation_time)

                # Étape 2: Déclencher la génération
                logger.info("=== Déclenchement de la génération ===")
                await self.trigger_generation()

                # Étape 3: Attendre l'heure de récupération (8h00)
                logger.info("=== Attente de l'heure de récupération ===")
                await self.wait_until_time(self.fetch_time)

                # Étape 4: Récupérer et envoyer le résumé
                logger.info("=== Récupération et envoi du résumé ===")
                await self.fetch_and_send_summary()

                # Attendre un peu pour éviter les exécutions multiples
                await asyncio.sleep(60)

            except Exception as e:
                logger.error(f"Erreur dans la boucle principale: {e}")
                await asyncio.sleep(300)  # Attendre 5 minutes en cas d'erreur

    def stop(self):
        """Arrête le bot"""
        self.running = False
        logger.info("Arrêt du bot...")


async def main():
    """Point d'entrée principal"""
    # Vérification de la configuration
    if not all([DUST_WORKSPACE_ID, DUST_API_KEY, DUST_CONVERSATION_ID, DUST_AGENT_ID, DISCORD_WEBHOOK_URL]):
        logger.error("Configuration incomplète. Vérifiez le fichier .env")
        logger.error(f"  DUST_WORKSPACE_ID: {'OK' if DUST_WORKSPACE_ID else 'MANQUANT'}")
        logger.error(f"  DUST_API_KEY: {'OK' if DUST_API_KEY else 'MANQUANT'}")
        logger.error(f"  DUST_CONVERSATION_ID: {'OK' if DUST_CONVERSATION_ID else 'MANQUANT'}")
        logger.error(f"  DUST_AGENT_ID: {'OK' if DUST_AGENT_ID else 'MANQUANT'}")
        logger.error(f"  DISCORD_WEBHOOK_URL: {'OK' if DISCORD_WEBHOOK_URL else 'MANQUANT'}")
        return

    bot = DailyNewsBot()

    try:
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Interruption détectée")
        bot.stop()


if __name__ == "__main__":
    asyncio.run(main())
