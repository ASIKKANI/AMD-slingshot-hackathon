import logging
from twilio.rest import Client
from config import settings
from scratchpad import scratchpad

logger = logging.getLogger(__name__)

class SMSFallbackOrchestrator:
    """
    Sends compressed critical data via SMS when internet connection goes dead.
    Allows orchestration commands to flow bi-directionally via Twilio gateway in dead zones.
    """
    def __init__(self):
        try:
            self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # Basic validation
            if "dummy" in settings.TWILIO_ACCOUNT_SID:
                raise ValueError("Dummy keys")
            self.is_configured = True
        except Exception as e:
            logger.warning("Twilio not configured properly. SMS Fallback operating in dry-run mode.")
            self.is_configured = False

    def check_network_and_trigger(self):
        """To be called periodically to check if we've been offline too long (e.g., > 5 mins)."""
        status = scratchpad.get_state("network_status")
        if status == "offline":
            logger.info("SMS Fallback: Extended network outage detected. Compressing local state for SMS dispatch.")
            self.dispatch_critical_payload()

    def dispatch_critical_payload(self):
        # Compress state dramatically
        earnings = scratchpad.get_state("daily_earnings") or 0.0
        location = scratchpad.get_state("current_location") or "unknown"
        
        # Super dense payload format to fit comfortably in a 160-char SMS window
        payload = f"SYNC|E:{earnings}|L:{location}"
        
        if self.is_configured:
            try:
                message = self.client.messages.create(
                    body=payload,
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to="+919999999999" # Targeting centralized gateway number
                )
                logger.info(f"SMS Fallback: Payload dispatched over cellular voice band. SMS SID: {message.sid}")
            except Exception as e:
                logger.error(f"SMS Fallback Failed to transmit: {e}")
        else:
            logger.info(f"[DRY RUN] SMS Fallback would have sent payload string: {payload}")

# Singleton
sms_fallback = SMSFallbackOrchestrator()
