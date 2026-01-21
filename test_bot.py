"""
Script de test pour vérifier le fonctionnement du bot sans attendre l'heure programmée
Simule le workflow: trigger à 7h58 → fetch à 8h00
"""
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv
import os

from dust_client import DustClient
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
DUST_CONVERSATION_ID = os.getenv('DUST_CONVERSATION_ID')
DUST_AGENT_ID = os.getenv('DUST_AGENT_ID')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

# Temps d'attente entre génération et récupération (en secondes)
WAIT_TIME = 120  # 2 minutes comme en prod (7h58 → 8h00)


async def test_trigger_generation():
    """Test du déclenchement de la génération"""
    logger.info("=== Test: Déclenchement de la génération ===")
    client = DustClient(DUST_WORKSPACE_ID, DUST_API_KEY)

    logger.info(f"Envoi du message à l'agent {DUST_AGENT_ID} dans la conversation {DUST_CONVERSATION_ID}")
    success = await client.trigger_daily_summary(DUST_CONVERSATION_ID, DUST_AGENT_ID)

    if success:
        logger.info("✅ Génération déclenchée avec succès")
        return True
    else:
        logger.error("❌ Échec du déclenchement de la génération")
        return False


async def test_fetch_last_message():
    """Test de la récupération du dernier message"""
    logger.info("\n=== Test: Récupération du dernier message ===")
    client = DustClient(DUST_WORKSPACE_ID, DUST_API_KEY)

    logger.info(f"Récupération du dernier message de l'agent depuis la conversation {DUST_CONVERSATION_ID}")
    message = await client.fetch_last_agent_message(DUST_CONVERSATION_ID)

    if message:
        logger.info(f"✅ Message récupéré ({len(message)} caractères)")
        logger.info(f"Aperçu: {message[:300]}...")
        return True, message
    else:
        logger.error("❌ Aucun message récupéré")
        return False, None


async def test_discord_webhook():
    """Test d'envoi de message sur Discord"""
    logger.info("\n=== Test: Webhook Discord ===")

    try:
        payload = {
            "content": "🧪 Test de connexion du bot - Si vous voyez ce message, le webhook fonctionne !",
            "username": "Dust Daily News Test"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(DISCORD_WEBHOOK_URL, json=payload) as response:
                if response.status in (200, 204):
                    logger.info("✅ Message de test envoyé avec succès sur Discord")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Erreur webhook Discord: {response.status} - {error_text}")
                    return False
    except Exception as e:
        logger.error(f"❌ Exception lors du test webhook: {e}")
        return False


async def test_full_workflow():
    """Test du workflow complet: trigger → wait → fetch → send"""
    logger.info("\n" + "=" * 60)
    logger.info("=== TEST DU WORKFLOW COMPLET ===")
    logger.info("=" * 60)

    client = DustClient(DUST_WORKSPACE_ID, DUST_API_KEY)

    # Étape 1: Déclencher la génération
    logger.info("\n📤 ÉTAPE 1: Déclenchement de la génération")
    success = await client.trigger_daily_summary(DUST_CONVERSATION_ID, DUST_AGENT_ID)
    if not success:
        logger.error("❌ Échec du déclenchement - Arrêt du test")
        return False

    # Étape 2: Attendre que l'agent génère sa réponse
    logger.info(f"\n⏳ ÉTAPE 2: Attente de {WAIT_TIME} secondes pour la génération...")
    for i in range(WAIT_TIME, 0, -30):
        logger.info(f"   {i} secondes restantes...")
        await asyncio.sleep(min(30, i))

    # Étape 3: Récupérer le dernier message
    logger.info("\n📥 ÉTAPE 3: Récupération du dernier message de l'agent")
    summary = await client.fetch_last_agent_message(DUST_CONVERSATION_ID)

    if not summary:
        logger.error("❌ Aucun message récupéré - Arrêt du test")
        return False

    logger.info(f"✅ Message récupéré ({len(summary)} caractères)")

    # Étape 4: Envoyer sur Discord
    logger.info("\n📨 ÉTAPE 4: Envoi sur Discord")
    today = datetime.now().strftime('%d/%m/%Y')

    # Discord limite à 2000 caractères par message
    header = f"📰 **Résumé quotidien - {today}**\n\n"
    max_content_length = 1900  # Marge pour le header

    # Découper le message si nécessaire
    messages = []
    if len(summary) <= max_content_length:
        messages.append(header + summary)
    else:
        messages.append(header + summary[:max_content_length] + "...")
        remaining = summary[max_content_length:]
        while remaining:
            chunk = remaining[:1900]
            remaining = remaining[1900:]
            messages.append(chunk + ("..." if remaining else ""))

    try:
        async with aiohttp.ClientSession() as session:
            for i, msg in enumerate(messages):
                payload = {
                    "content": msg,
                    "username": "Dust Daily News Test"
                }
                async with session.post(DISCORD_WEBHOOK_URL, json=payload) as response:
                    if response.status not in (200, 204):
                        logger.error(f"❌ Échec de l'envoi sur Discord (partie {i+1}): {response.status}")
                        return False

            logger.info(f"✅ Résumé envoyé avec succès sur Discord ({len(messages)} message(s))")
            return True
    except Exception as e:
        logger.error(f"❌ Exception lors de l'envoi: {e}")
        return False


async def main():
    """Exécute les tests"""
    logger.info("🚀 Démarrage des tests du bot Discord News\n")

    # Vérification de la configuration
    if not all([DUST_WORKSPACE_ID, DUST_API_KEY, DUST_CONVERSATION_ID, DUST_AGENT_ID, DISCORD_WEBHOOK_URL]):
        logger.error("❌ Configuration incomplète. Vérifiez le fichier .env")
        logger.error(f"  DUST_WORKSPACE_ID: {'OK' if DUST_WORKSPACE_ID else 'MANQUANT'}")
        logger.error(f"  DUST_API_KEY: {'OK' if DUST_API_KEY else 'MANQUANT'}")
        logger.error(f"  DUST_CONVERSATION_ID: {'OK' if DUST_CONVERSATION_ID else 'MANQUANT'}")
        logger.error(f"  DUST_AGENT_ID: {'OK' if DUST_AGENT_ID else 'MANQUANT'}")
        logger.error(f"  DISCORD_WEBHOOK_URL: {'OK' if DISCORD_WEBHOOK_URL else 'MANQUANT'}")
        return

    logger.info("Configuration:")
    logger.info(f"  - Workspace ID: {DUST_WORKSPACE_ID}")
    logger.info(f"  - Conversation ID: {DUST_CONVERSATION_ID}")
    logger.info(f"  - Agent ID: {DUST_AGENT_ID}")
    logger.info(f"  - Temps d'attente: {WAIT_TIME} secondes")
    logger.info(f"  - Webhook configuré: Oui\n")

    # Test du workflow complet
    result = await test_full_workflow()

    # Résumé
    logger.info("\n" + "=" * 60)
    logger.info("RÉSULTAT FINAL")
    logger.info("=" * 60)
    if result:
        logger.info("🎉 Workflow complet réussi !")
        logger.info("Le bot est prêt pour la production.")
    else:
        logger.info("⚠️ Le workflow a échoué.")
        logger.info("Vérifiez les logs ci-dessus pour identifier le problème.")


if __name__ == "__main__":
    asyncio.run(main())
