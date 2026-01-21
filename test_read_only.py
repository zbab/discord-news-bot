"""
Script de test en lecture seule - ne fait que lire la dernière réponse
"""
import asyncio
import logging
from dotenv import load_dotenv
import os
from dust_client import DustClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

DUST_WORKSPACE_ID = os.getenv('DUST_WORKSPACE_ID')
DUST_API_KEY = os.getenv('DUST_API_KEY')
DUST_CONVERSATION_ID = os.getenv('DUST_CONVERSATION_ID')


async def test_read_conversation():
    """Lit simplement la dernière réponse de la conversation"""
    logger.info("=== Test de lecture de la conversation ===\n")

    client = DustClient(DUST_WORKSPACE_ID, DUST_API_KEY)

    logger.info(f"Lecture de la conversation: {DUST_CONVERSATION_ID}")
    summary = await client.get_conversation(DUST_CONVERSATION_ID)

    if summary:
        logger.info(f"\n✅ Dernière réponse trouvée ({len(summary)} caractères)")
        logger.info(f"\n--- CONTENU ---")
        logger.info(summary)
        logger.info("--- FIN ---\n")
    else:
        logger.warning("⚠️ Aucune réponse d'agent trouvée dans la conversation")


async def main():
    logger.info("Test en lecture seule\n")

    if not all([DUST_WORKSPACE_ID, DUST_API_KEY, DUST_CONVERSATION_ID]):
        logger.error("❌ Configuration incomplète")
        return

    await test_read_conversation()


if __name__ == "__main__":
    asyncio.run(main())
