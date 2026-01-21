"""
Script de test simplifié pour éviter les rate limits
"""
import asyncio
import logging
from dotenv import load_dotenv
import os
from dust_client import DustClient
import aiohttp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

DUST_WORKSPACE_ID = os.getenv('DUST_WORKSPACE_ID')
DUST_API_KEY = os.getenv('DUST_API_KEY')
DUST_CONVERSATION_ID = os.getenv('DUST_CONVERSATION_ID')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')


async def test_single_workflow():
    """Test du workflow complet avec attente"""
    logger.info("=== Test du workflow complet (avec attente pour l'agent) ===\n")

    client = DustClient(DUST_WORKSPACE_ID, DUST_API_KEY)

    # 1. Envoyer le message
    logger.info("1. Envoi du message à l'agent Dust...")
    success = await client.post_message_to_conversation(
        DUST_CONVERSATION_ID,
        "Peux-tu me donner un résumé rapide des actualités importantes des réseaux sociaux ?"
    )

    if not success:
        logger.error("❌ Échec de l'envoi du message")
        return

    logger.info("✅ Message envoyé avec succès")

    # 2. Attendre la réponse de l'agent
    logger.info("\n2. Attente de la réponse de l'agent (15 secondes)...")
    await asyncio.sleep(15)

    # 3. Récupérer les événements
    logger.info("\n3. Récupération de la réponse...")
    summary = await client.get_conversation_events(DUST_CONVERSATION_ID)

    if summary:
        logger.info(f"\n✅ Résumé récupéré ({len(summary)} caractères)")
        logger.info(f"\n--- CONTENU DU RÉSUMÉ ---")
        logger.info(summary)
        logger.info("--- FIN DU RÉSUMÉ ---\n")

        # 4. Envoyer sur Discord
        logger.info("4. Envoi sur Discord...")
        payload = {
            "content": f"📰 **Test de résumé quotidien**\n\n{summary}",
            "username": "Dust Daily News"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(DISCORD_WEBHOOK_URL, json=payload) as response:
                if response.status in (200, 204):
                    logger.info("✅ Résumé envoyé avec succès sur Discord")
                else:
                    logger.error(f"❌ Échec de l'envoi sur Discord: {response.status}")
    else:
        logger.error("❌ Impossible de récupérer le résumé")


async def main():
    logger.info("Test simplifié du bot Discord News\n")

    if not all([DUST_WORKSPACE_ID, DUST_API_KEY, DUST_CONVERSATION_ID, DISCORD_WEBHOOK_URL]):
        logger.error("❌ Configuration incomplète")
        return

    await test_single_workflow()


if __name__ == "__main__":
    asyncio.run(main())
