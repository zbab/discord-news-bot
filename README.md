# Discord News Bot

Bot Discord pour récupérer automatiquement un résumé quotidien depuis l'agent Dust "Actualité-réseaux" et l'envoyer sur Discord.

## Fonctionnalités

- 📰 Récupération quotidienne d'un résumé depuis l'agent Dust
- 🤖 Envoi automatique sur Discord via webhook
- ⏰ Planification à heure fixe (configurable)
- 📝 Logs détaillés

## Installation

1. Activer l'environnement virtuel:
```bash
source venv/bin/activate
```

2. Installer les dépendances (si nécessaire):
```bash
pip install -r requirements.txt
```

3. Configurer le fichier `.env` avec vos credentials (déjà configuré)

## Configuration

Le fichier `.env` contient:
- `DUST_WORKSPACE_ID`: ID de votre workspace Dust
- `DUST_API_KEY`: Clé API Dust
- `DUST_CONVERSATION_ID`: ID de la conversation avec l'agent
- `DISCORD_WEBHOOK_URL`: URL du webhook Discord
- `DAILY_SUMMARY_TIME`: Heure d'envoi au format HH:MM (défaut: 08:00)

## Utilisation

### Lancer le bot en production

```bash
python bot.py
```

Le bot va:
1. Se connecter à l'API Dust
2. Attendre l'heure programmée (8h00 par défaut)
3. Envoyer un message à l'agent dans la conversation
4. Attendre la réponse (15 secondes)
5. Récupérer le résumé
6. L'envoyer sur Discord
7. Répéter quotidiennement

### Tests disponibles

**Test de lecture seule** (ne consomme pas de requête API):
```bash
python test_read_only.py
```

**Test complet** (avec envoi de message):
```bash
python test_simple.py
```

**Test de structure** (debug):
```bash
python test_conversation_structure.py
```

## Architecture

### Fichiers principaux

- [bot.py](bot.py) : Bot principal avec scheduler quotidien
- [dust_client.py](dust_client.py) : Client pour l'API Dust
- [.env](.env) : Configuration (ne pas committer)

### Fichiers de test

- [test_bot.py](test_bot.py) : Suite de tests complète
- [test_simple.py](test_simple.py) : Test workflow simplifié
- [test_read_only.py](test_read_only.py) : Test lecture conversation
- [test_conversation_structure.py](test_conversation_structure.py) : Debug structure API

## Notes importantes

### Rate Limits

L'API Dust a des limites de taux. Si vous obtenez une erreur 403 avec "rate_limit_error":
- Attendez quelques minutes avant de réessayer
- Utilisez `test_read_only.py` pour tester sans consommer de requêtes d'écriture

### Structure de la conversation Dust

La conversation suit cette structure:
```json
{
  "conversation": {
    "content": [
      [
        {
          "type": "user_message" ou "agent_message",
          "content": "Le contenu du message..."
        }
      ]
    ]
  }
}
```

Le bot récupère le dernier message avec `type: "agent_message"`.

## Prochaines étapes

- [ ] Ajouter le scraping de X (Twitter)
- [ ] Gestion des erreurs améliorée avec retry
- [ ] Support de multiples agents
- [ ] Configuration de multiples canaux Discord
- [ ] Mécanisme de polling plus intelligent pour détecter la fin de réponse de l'agent

## Logs

Les logs sont affichés dans la console avec le format:
```
YYYY-MM-DD HH:MM:SS - module - LEVEL - message
```

Niveaux:
- INFO: Opérations normales
- WARNING: Avertissements non bloquants
- ERROR: Erreurs nécessitant attention
