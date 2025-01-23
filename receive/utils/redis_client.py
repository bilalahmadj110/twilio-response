import redis
from redis.connection import ConnectionPool
from config import Config
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    """Redis client with connection pooling."""
    
    def __init__(self):
        self.pool = ConnectionPool(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            password=Config.REDIS_PASSWORD,
            db=Config.REDIS_DB,
            decode_responses=True
        )
        self.client = redis.Redis(connection_pool=self.pool)

    def is_connected(self) -> bool:
        """Check Redis connection."""
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Redis connection error: {e}")
            return False

    def store_message(self, phone: str, message: str) -> bool:
        """Store message interaction."""
        try:
            key = f"message:{phone}:{int(time.time())}"
            self.client.setex(key, 86400, message)  # Expire after 24 hours
            return True
        except Exception as e:
            logger.error(f"Error storing message: {e}")
            return False
