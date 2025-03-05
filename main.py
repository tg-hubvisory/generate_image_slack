import os
import time
import logging
import replicate
import requests
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse

# Load environment variables
load_dotenv()

# Constants
CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
MODEL_NAME = "black-forest-labs/flux-1.1-pro-ultra"
BOT_USER_ID = os.getenv("SLACK_BOT_USER_ID")

# Initialize clients
client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
socket_client = SocketModeClient(
    app_token=os.environ["SLACK_APP_TOKEN"],
    web_client=client
)

logging.getLogger('faiss').setLevel(logging.WARNING)

# Stocke les prompts en attente d'un ratio
pending_prompts = {}

RATIOS = ["21:9", "16:9", "3:2", "4:3", "5:4", "1:1", "4:5", "3:4", "2:3", "9:16", "9:21"]

def generate_image_from_replicate(prompt: str, aspect_ratio: str) -> str:
    """Generate an image using Replicate API and return the image URL."""
    try:
        output = replicate.run(
            MODEL_NAME,
            input={
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "prompt_upsampling": True
            }
        )
        return output[0] if isinstance(output, list) else output
    except Exception as e:
        logging.error(f"Erreur lors de l'appel à Replicate: {e}")
        return ""

def process_message_events(client: SocketModeClient, req: SocketModeRequest):
    if req.type == "events_api":
        # Acknowledge the request
        response = SocketModeResponse(envelope_id=req.envelope_id)
        client.send_socket_mode_response(response)
        
        # Process the event
        payload = req.payload
        event = payload.get("event", {})
        if event.get("type") == "message" and event.get("channel") == CHANNEL_ID:
            user_id = event.get("user", "")
            if user_id == BOT_USER_ID:
                return  # Ignore messages sent by the bot itself
            
            message = event.get('text', '').strip()
            if not message:
                return
            
            # Vérifie si l'utilisateur a un prompt en attente et valide son ratio
            if user_id in pending_prompts:
                if message in RATIOS:
                    prompt = pending_prompts.pop(user_id)
                    print(f"\n👤 [{user_id}]: {prompt} (Ratio: {message})")
                    image_url = generate_image_from_replicate(prompt, message)
                    
                    if image_url:
                        try:
                            response = requests.get(image_url)
                            if response.status_code == 200:
                                image_path = "output.jpg"
                                with open(image_path, "wb") as file:
                                    file.write(response.content)
                                
                                client.web_client.files_upload_v2(
                                    channels=CHANNEL_ID,
                                    file=image_path,
                                    title="Image générée",
                                    initial_comment=f"<@{user_id}> Et voilà le travail ⚡"
                                )
                                os.remove(image_path)
                            else:
                                raise Exception("Échec du téléchargement de l'image.")
                        except Exception as e:
                            logging.error(f"Erreur lors de l'envoi de l'image sur Slack: {e}")
                            client.web_client.chat_postMessage(channel=CHANNEL_ID, text="❌ Une erreur est survenue lors de la génération de l'image.")
                    else:
                        client.web_client.chat_postMessage(channel=CHANNEL_ID, text="❌ Une erreur est survenue lors de la génération de l'image.")
                else:
                    client.web_client.chat_postMessage(channel=CHANNEL_ID, text="⚠️ Merci de répondre avec l'un des ratios valides : " + ", ".join(RATIOS))
                return
            
            # Vérifie si le message commence par "generate " (sans /)
            if message.lower().startswith("generate "):
                prompt = message[len("generate "):].strip()
                if not prompt:
                    client.web_client.chat_postMessage(channel=CHANNEL_ID, text="⚠️ Merci de fournir un prompt après `generate`.")
                    return
                
                # Enregistrer le prompt et demander le ratio
                pending_prompts[user_id] = prompt
                client.web_client.chat_postMessage(channel=CHANNEL_ID, text="🖼 Quel ratio souhaitez-vous ? Répondez avec l'un des choix suivants : " + ", ".join(RATIOS))

def main():
    print(f"⚙️ Démarrage du script pour le canal {CHANNEL_ID}...")
    
    # Test channel access
    try:
        result = client.conversations_info(channel=CHANNEL_ID)
        channel_name = result["channel"].get("name", "Inconnu")
        print(f"Connecté au canal: #{channel_name}")
    except SlackApiError as e:
        print(f"Erreur lors de l'accès au canal {CHANNEL_ID}: {e}")
        return
    
    # Register event handler
    socket_client.socket_mode_request_listeners.append(process_message_events)
    
    # Start listening
    print("Ecoute des messages. Appuyez sur Ctrl+C pour arrêter.")
    socket_client.connect()
    
    # Keep the script running
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
