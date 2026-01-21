"""
Script de debug pour voir le format exact des événements
"""
import asyncio
import logging
from dotenv import load_dotenv
import os
import aiohttp

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

DUST_WORKSPACE_ID = os.getenv('DUST_WORKSPACE_ID')
DUST_API_KEY = os.getenv('DUST_API_KEY')
DUST_CONVERSATION_ID = os.getenv('DUST_CONVERSATION_ID')


async def debug_events():
    """Debug des événements de la conversation"""
    url = f"https://dust.tt/api/v1/w/{DUST_WORKSPACE_ID}/assistant/conversations/{DUST_CONVERSATION_ID}/events"
    headers = {
        "Authorization": f"Bearer {DUST_API_KEY}",
        "Content-Type": "application/json"
    }

    logger.info(f"Requête: {url}")

    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as response:
                logger.info(f"Status: {response.status}")
                logger.info(f"Headers: {response.headers}")

                if response.status == 200:
                    # Lire par morceaux pour voir si c'est un stream
                    logger.info("\n--- Contenu brut (premiers 5000 caractères) ---")
                    content = await response.text()
                    logger.info(content[:5000])
                    logger.info(f"\n--- Total: {len(content)} caractères ---")
                else:
                    error = await response.text()
                    logger.error(f"Erreur: {error}")

    except asyncio.TimeoutError:
        logger.error("Timeout lors de la requête")
    except Exception as e:
        logger.error(f"Exception: {e}")


async def main():
    logger.info("Debug des événements de conversation\n")
    await debug_events()


if __name__ == "__main__":
    asyncio.run(main())
