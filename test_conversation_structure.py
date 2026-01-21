"""
Script pour debugger la structure de la conversation
"""
import asyncio
import logging
import json
from dotenv import load_dotenv
import os
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


async def debug_conversation_structure():
    """Debug de la structure de la conversation"""
    url = f"https://dust.tt/api/v1/w/{DUST_WORKSPACE_ID}/assistant/conversations/{DUST_CONVERSATION_ID}"
    headers = {
        "Authorization": f"Bearer {DUST_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()

                    # Sauvegarder la structure complète
                    with open('conversation_structure.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)

                    logger.info("✅ Structure sauvegardée dans conversation_structure.json")

                    # Afficher un aperçu
                    conversation = data.get("conversation", {})
                    logger.info(f"\nClés principales: {list(conversation.keys())}")

                    content = conversation.get("content", [])
                    logger.info(f"Nombre d'items dans content: {len(content)}")

                    # Explorer les premiers items
                    for i, item in enumerate(content[:3]):
                        logger.info(f"\n--- Item {i} ---")
                        logger.info(f"Type: {type(item)}")
                        if isinstance(item, list):
                            logger.info(f"Longueur de la liste: {len(item)}")
                            if len(item) > 0:
                                logger.info(f"Premier élément: {type(item[0])}")
                                if isinstance(item[0], dict):
                                    logger.info(f"Clés: {list(item[0].keys())}")
                                    logger.info(f"Contenu: {json.dumps(item[0], indent=2, ensure_ascii=False)[:500]}")
                        elif isinstance(item, dict):
                            logger.info(f"Clés: {list(item.keys())}")

                else:
                    error = await response.text()
                    logger.error(f"Erreur: {response.status} - {error}")

    except Exception as e:
        logger.error(f"Exception: {e}")


async def main():
    logger.info("Debug de la structure de conversation\n")
    await debug_conversation_structure()


if __name__ == "__main__":
    asyncio.run(main())
