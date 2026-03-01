import time
from loguru import logger
from twilio.rest import Client
from backend.scratchpad import scratchpad

class SmsFallbackModule:
    """Ensures intelligence loop continues over SMS during data outages."""
    
    def __init__(self, account_sid=None, auth_token=None):
        self.client = Client(account_sid, auth_token) if account_sid else None
        self.last_sync_time = time.time()

    def check_connectivity(self):
        # Simulated connectivity check
        network = scratchpad.get_state("network_status")
        if network == "OFFLINE" and (time.time() - self.last_sync_time) > 300:
            self.trigger_sms_fallback()

    def trigger_sms_fallback(self):
        earnings = scratchpad.get_state("daily_earnings")
        hotspot = scratchpad.get_state("last_known_hotspot")
        
        # Compressed payload for SMS (160 characters)
        payload = f"Sahayak: Earn:₹{earnings}|Next:{hotspot}|Alert:OFFLINE"
        
        if self.client:
            self.client.messages.create(body=payload, from_='+123456789', to='+919876543210')
            logger.info(f"SMS Fallback Triggered: {payload}")
        else:
            logger.warning(f"SMS Gateway Not Configured. Payload: {payload}")

    async def run_loop(self):
        while True:
            self.check_connectivity()
            await asyncio.sleep(60)
