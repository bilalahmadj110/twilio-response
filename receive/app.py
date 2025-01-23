from flask import Flask, request, abort
from twilio.twiml.messaging_response import MessagingResponse
from utils.redis_client import RedisClient
from utils.message_handler import MessageHandler
from utils.webhook_auth import validate_twilio_request
from config import Config
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Redis client
redis_client = RedisClient()
message_handler = MessageHandler(redis_client)

@app.route("/webhook", methods=['POST'])
@validate_twilio_request
def webhook():
    """Handle incoming SMS messages."""
    try:
        # Extract message details
        incoming_msg = request.form.get('Body', '').lower()
        sender_phone = request.form.get('From', '')
        
        # Create response object
        resp = MessagingResponse()

        # Process message
        should_reply = message_handler.should_send_auto_reply(incoming_msg)
        
        if should_reply:
            # Send auto-reply
            message = resp.message(app.config['AUTO_REPLY_MESSAGE'])
            
            # Store interaction in Redis
            message_handler.store_interaction(sender_phone, incoming_msg)
            
            logger.info(f"Auto-reply sent to {sender_phone}")
        else:
            logger.info(f"No auto-reply needed for message from {sender_phone}")

        return str(resp)

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return str(MessagingResponse())

@app.route("/", methods=['GET'])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "redis": redis_client.is_connected()}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
