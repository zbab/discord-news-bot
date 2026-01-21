"""
Script de démonstration du workflow complet
Utilise le dernier message existant pour simuler le workflow sans rate limit
"""
import asyncio
import logging
from dotenv import load_dotenv
import os
from dust_client import DustClient
import aiohttp
from datetime import datetime

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


async def demo_workflow():
    """Démo du workflow complet avec le dernier message existant"""
    logger.info("=== DÉMONSTRATION DU WORKFLOW COMPLET ===\n")

    client = DustClient(DUST_WORKSPACE_ID, DUST_API_KEY)

    # 1. Simuler la récupération d'un résumé
    logger.info("1. Récupération du dernier résumé de l'agent Dust...")
    summary = await client.get_conversation(DUST_CONVERSATION_ID)

    if not summary:
        logger.error("❌ Impossible de récupérer le résumé")
        return

    logger.info(f"✅ Résumé récupéré ({len(summary)} caractères)")
    logger.info(f"\n--- APERÇU DU CONTENU ---")
    logger.info(summary[:300] + "..." if len(summary) > 300 else summary)
    logger.info("--- FIN APERÇU ---\n")

    # 2. Formater le message comme le ferait le bot
    logger.info("2. Formatage du message pour Discord...")
    today = datetime.now().strftime('%d/%m/%Y')
    discord_message = f"📰 **Résumé quotidien - {today}**\n\n{summary}"

    logger.info(f"✅ Message formaté ({len(discord_message)} caractères)")

    # 3. Envoyer sur Discord
    logger.info("\n3. Envoi du résumé sur Discord...")
    try:
        payload = {
            "content": discord_message[:2000],  # Discord limite à 2000 caractères
            "username": "Dust Daily News"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(DISCORD_WEBHOOK_URL, json=payload) as response:
                if response.status in (200, 204):
                    logger.info("✅ Résumé envoyé avec succès sur Discord")

                    logger.info("\n" + "="*60)
                    logger.info("✅ WORKFLOW COMPLET TERMINÉ AVEC SUCCÈS")
                    logger.info("="*60)
                    logger.info("\nCe que le bot fera automatiquement chaque jour à 8h00:")
                    logger.info("  1. ✅ Envoyer une question à l'agent Dust")
                    logger.info("  2. ✅ Attendre 60 secondes pour la génération")
                    logger.info("  3. ✅ Récupérer le résumé")
                    logger.info("  4. ✅ Envoyer sur Discord")
                    logger.info("\nVous pouvez maintenant lancer le bot en production avec:")
                    logger.info("  python bot.py")

                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Échec de l'envoi sur Discord: {response.status} - {error_text}")
                    return False
    except Exception as e:
        logger.error(f"❌ Exception lors de l'envoi sur Discord: {e}")
        return False


async def main():
    logger.info("Démonstration du bot Discord News\n")

    if not all([DUST_WORKSPACE_ID, DUST_API_KEY, DUST_CONVERSATION_ID, DISCORD_WEBHOOK_URL]):
        logger.error("❌ Configuration incomplète")
        return

    await demo_workflow()


if __name__ == "__main__":
    asyncio.run(main())
