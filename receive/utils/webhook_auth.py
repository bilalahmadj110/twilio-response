from functools import wraps
from flask import request, abort
from twilio.request_validator import RequestValidator
from config import Config
import logging

logger = logging.getLogger(__name__)

def validate_twilio_request(f):
    """Validates that incoming requests genuinely originated from Twilio"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Create validator
        validator = RequestValidator(Config.TWILIO_AUTH_TOKEN)

        # Validate request
        twilio_signature = request.headers.get('X-Twilio-Signature', '')
        url = Config.WEBHOOK_URL + request.path
        
        # Get POST parameters
        post_data = request.form.copy()
        
        # Validate request
        try:
            is_valid = validator.validate(
                url,
                post_data,
                twilio_signature
            )
        except Exception as e:
            logger.error(f"Webhook validation error: {e}")
            is_valid = False

        if not is_valid:
            logger.warning("Invalid Twilio signature. Request rejected.")
            abort(403)

        return f(*args, **kwargs)
    return decorated_function
