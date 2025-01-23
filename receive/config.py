import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    
    OPT_IN_WORDS = [word.strip() for word in 
                    os.getenv('OPT_IN_WORDS', '').split(',')]
    AUTO_REPLY_MESSAGE = os.getenv('AUTO_REPLY_MESSAGE', 
                                  'Thank you for subscribing!')
    
    # Webhook configuration
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', 'http://localhost:5000')
