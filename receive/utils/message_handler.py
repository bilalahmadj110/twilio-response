from config import Config
from utils.redis_client import RedisClient
import logging
import time

logger = logging.getLogger(__name__)

class MessageHandler:
    """Handle message processing and auto-reply logic."""
    
    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client
        self.opt_in_words = Config.OPT_IN_WORDS

    def should_send_auto_reply(self, message: str) -> bool:
        """Check if message contains opt-in words."""
        return any(word in message.lower() for word in self.opt_in_words)

    def store_interaction(self, phone: str, message: str) -> bool:
        """Store interaction in Redis."""
        return self.redis_client.store_message(phone, message)
