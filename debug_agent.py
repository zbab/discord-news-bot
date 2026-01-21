"""
Script de debug pour lister tous les agents disponibles
"""
import asyncio
import logging
from dotenv import load_dotenv
import os
import aiohttp

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
DUST_AGENT_NAME = os.getenv('DUST_AGENT_NAME')


async def list_all_agents():
    """Liste tous les agents du workspace"""
    url = f"https://dust.tt/api/v1/w/{DUST_WORKSPACE_ID}/assistant/agent_configurations"
    headers = {
        "Authorization": f"Bearer {DUST_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    agents = data.get("agentConfigurations", [])

                    logger.info(f"Nombre d'agents trouvés: {len(agents)}\n")

                    for i, agent in enumerate(agents, 1):
                        name = agent.get("name", "N/A")
                        sid = agent.get("sId", "N/A")
                        description = agent.get("description", "N/A")

                        logger.info(f"Agent #{i}:")
                        logger.info(f"  Nom: {name}")
                        logger.info(f"  ID (sId): {sid}")
                        logger.info(f"  Description: {description}")
                        logger.info("")

                    return agents
                else:
                    error_text = await response.text()
                    logger.error(f"Erreur: {response.status} - {error_text}")
                    return []
    except Exception as e:
        logger.error(f"Exception: {e}")
        return []


async def search_agent(query):
    """Recherche un agent"""
    url = f"https://dust.tt/api/v1/w/{DUST_WORKSPACE_ID}/assistant/agent_configurations/search"
    headers = {
        "Authorization": f"Bearer {DUST_API_KEY}",
        "Content-Type": "application/json"
    }
    params = {"q": query}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    agents = data.get("agentConfigurations", [])

                    logger.info(f"Recherche pour '{query}': {len(agents)} résultat(s)\n")

                    for i, agent in enumerate(agents, 1):
                        name = agent.get("name", "N/A")
                        sid = agent.get("sId", "N/A")

                        logger.info(f"Résultat #{i}:")
                        logger.info(f"  Nom: {name}")
                        logger.info(f"  ID: {sid}")
                        logger.info("")

                    return agents
                else:
                    error_text = await response.text()
                    logger.error(f"Erreur: {response.status} - {error_text}")
                    return []
    except Exception as e:
        logger.error(f"Exception: {e}")
        return []


async def main():
    logger.info("=== DEBUG: Agents Dust ===\n")

    # Liste tous les agents
    logger.info("--- LISTE COMPLÈTE DES AGENTS ---")
    all_agents = await list_all_agents()

    # Recherche l'agent configuré
    logger.info(f"--- RECHERCHE POUR '{DUST_AGENT_NAME}' ---")
    search_results = await search_agent(DUST_AGENT_NAME)

    # Recherche avec différentes variantes
    logger.info("--- RECHERCHE AVEC VARIANTES ---")
    for variant in ["Actualité", "actualité", "réseaux", "news"]:
        logger.info(f"\nRecherche: '{variant}'")
        await search_agent(variant)


if __name__ == "__main__":
    asyncio.run(main())
