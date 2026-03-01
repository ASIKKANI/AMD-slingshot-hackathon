import redis
import json
import asyncio
from loguru import logger
from typing import Dict, Any, Optional
from backend.config import config

class SahayakScratchpad:
    """
    Central Nervous System for Multi-Agent coordination.
    Implements thread-safe Redis logic with a priority-based conflict resolution.
    """
    def __init__(self, host=config.REDIS_HOST, port=config.REDIS_PORT):
        self._pool = redis.ConnectionPool(host=host, port=port, db=0, decode_responses=True)
        self.r = redis.Redis(connection_pool=self._pool)
        logger.info(f"Connecting to Redis Scratchpad at {host}:{port}")

    async def update_state(self, key: str, value: Any):
        """Standard state update across the MAS."""
        try:
            current_val = self.r.get(key)
            # Conflict Resolution: Safety > Profit
            if key == "market_action" and value == "ACCEPT_ORDER":
                fatigue = float(self.r.get("fatigue_score") or 0.0)
                if fatigue >= config.FATIGUE_CRITICAL_THRESHOLD:
                    logger.warning(f"Conflict Resolution: Order Acceptance BLOCKED due to high fatigue ({fatigue})")
                    self.r.set("system_alert", "SAFETY_LOCK_ACTIVE")
                    return False
            
            self.r.set(key, json.dumps(value) if isinstance(value, (dict, list)) else str(value))
            return True
        except Exception as e:
            logger.error(f"Scratchpad Update Error: {e}")
            return False

    def get_state(self, key: str) -> Optional[Any]:
        """Retrieve state from the scratchpad."""
        val = self.r.get(key)
        if val is None:
            return None
        try:
            return json.loads(val)
        except:
            return val

    def get_full_context(self) -> Dict[str, Any]:
        """Snapshot of the entire worker state for MAS decision loops."""
        keys = ["current_location", "fatigue_score", "daily_earnings", "active_pings", "network_status", "system_alert"]
        return {k: self.get_state(k) for k in keys}

    async def wait_for_event(self, key: str, target_value: str, timeout: int = 10):
        """Asynchronous event-driven synchronization for agents."""
        start = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start) < timeout:
            if self.get_state(key) == target_value:
                return True
            await asyncio.sleep(0.5)
        return False

# Singleton instance for backend-wide usage
scratchpad = SahayakScratchpad()
