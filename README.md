# README - Bot Slack de génération d'images avec Replicate

## Description
Ce projet est un bot Slack permettant de générer des images à partir de prompts textuels en utilisant l'API Replicate. Il interagit avec les utilisateurs via un canal Slack en écoutant les messages et en répondant avec des images générées selon le ratio spécifié.

## Fonctionnalités
- Écoute des messages Slack dans un canal spécifié.
- Traitement des commandes utilisateur pour la génération d'images.
- Interaction avec l'API Replicate pour générer des images.
- Envoi automatique des images générées sur Slack.

## Prérequis
Avant d'exécuter le script, assurez-vous d'avoir :
- Un compte Slack et un bot configuré avec les permissions nécessaires.
- Un compte Replicate avec une clé API.
- Python 3 installé sur votre machine.

## Installation
1. Clonez ce dépôt :
   ```sh
   git clone https://github.com/tg-hubvisory/generate_image_slack.git
   cd generate_image_slack
   ```
2. Installez les dépendances requises :
   ```sh
   pip install -r requirements.txt
   ```
3. Configurez les variables d'environnement en créant un fichier `.env` :
   ```env
   SLACK_BOT_TOKEN=your-slack-bot-token
   SLACK_APP_TOKEN=your-slack-app-token
   SLACK_CHANNEL_ID=your-channel-id
   SLACK_BOT_USER_ID=your-bot-user-id
   REPLICATE_API_TOKEN=your-replicate-api-token
   ```

## Utilisation
1. Démarrez le bot :
   ```sh
   python main.py
   ```
2. Dans Slack, envoyez un message commençant par `generate ` suivi de votre prompt.
3. Le bot vous demandera de choisir un ratio parmi les valeurs disponibles.
4. Une fois le ratio fourni, l'image sera générée et envoyée sur Slack.

## Ratios supportés
Le bot prend en charge les ratios d'image suivants :
- 21:9
- 16:9
- 3:2
- 4:3
- 5:4
- 1:1
- 4:5
- 3:4
- 2:3
- 9:16
- 9:21

## Débogage et logs
- Pour voir les logs d'exécution, vous pouvez ajouter des impressions (`print`) ou utiliser le module `logging`.
- Si le bot ne répond pas, vérifiez que toutes les variables d'environnement sont correctement définies.
- Vérifiez que votre bot Slack est bien ajouté au canal spécifié.