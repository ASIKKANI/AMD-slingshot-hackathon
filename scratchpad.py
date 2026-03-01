import redis
import json
import threading
from typing import Dict, Any, Optional
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SharedScratchpad:
    """
    Central Nervous System for Project Sahayak MAS.
    Holds real-time variables and handles conflict resolution with strict Safety > Profit priorities.
    """
    def __init__(self):
        self.local_state: Dict[str, Any] = {
            "current_location": None,
            "active_pings": [],
            "fatigue_score": 0.0,
            "daily_earnings": 0.0,
            "current_app_state": "idle",
            "network_status": "online",
            "BLOCK_HIGH_STRESS_ORDERS": False,
            "petrol_cost_per_km": 2.5, # Default petrol cost
            "device_capability": "npu_capable" # "npu_capable" or "basic_cloud"
        }
        self.lock = threading.Lock()
        
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True,
                socket_timeout=2
            )
            self.redis_client.ping()
            self.use_redis = True
            logger.info("Connected to Redis Scratchpad.")
        except (redis.ConnectionError, redis.TimeoutError):
            logger.warning("Redis unavailable. Using in-memory local state (Offline-First mode).")
            self.use_redis = False

    def update_state(self, key: str, value: Any):
        """Update a variable in the scratchpad with thread safety."""
        with self.lock:
            # Conflict Resolution: Safety Overwrites Profit
            if key == "BLOCK_HIGH_STRESS_ORDERS" and value is True:
                logger.critical("SAFETY OVERRIDE: High stress detected. Blocking high-stress orders.")
                self.local_state["BLOCK_HIGH_STRESS_ORDERS"] = True
            
            # Fatigue Score Check - enforce Safety Override logic directly at state level
            if key == "fatigue_score" and isinstance(value, float) and value >= settings.CRITICAL_FATIGUE_THRESHOLD:
                logger.critical("SAFETY OVERRIDE: Critical fatigue margin reached.")
                self.local_state["BLOCK_HIGH_STRESS_ORDERS"] = True
            
            self.local_state[key] = value
            
            if self.use_redis:
                try:
                    if isinstance(value, (dict, list)):
                        self.redis_client.set(key, json.dumps(value))
                    else:
                        self.redis_client.set(key, value)
                except redis.RedisError as e:
                    logger.error(f"Redis sync failed for {key}: {e}")

    def get_state(self, key: str) -> Optional[Any]:
        """Retrieve a variable from the scratchpad."""
        if self.use_redis:
            try:
                val = self.redis_client.get(key)
                if val is not None:
                    try:
                        return json.loads(val)
                    except json.JSONDecodeError:
                        return val
            except redis.RedisError:
                pass # Fallback to local state
                
        with self.lock:
            return self.local_state.get(key)

# Global singleton instance for MAS to import and use
scratchpad = SharedScratchpad()
