import asyncio
import numpy as np
from loguru import logger
from backend.scratchpad import scratchpad
from backend.config import config

class BiometricSentinel:
    """Monitors driver safety using edge sensor analysis."""
    
    def detect_fatigue(self, sensor_batch: list):
        """
        In production, this would call an ONNX model optimized for AMD NPU.
        Simulating anomaly detection on accelerometer/gyro data.
        """
        # Example: Variability in steering (gyro) and erratic braking (accel)
        accel_variance = np.var([s['z_accel'] for s in sensor_batch])
        braking_events = sum(1 for s in sensor_batch if s['x_accel'] > 9.8) # High-G braking
        
        # High variance + hard braking = fatigue/stress
        fatigue_score = (accel_variance * 0.4) + (braking_events * 0.1)
        return min(fatigue_score, 1.0)

    async def monitor_safety(self, sensor_data):
        score = self.detect_fatigue(sensor_data)
        await scratchpad.update_state("fatigue_score", score)
        
        if score >= config.FATIGUE_CRITICAL_THRESHOLD:
            logger.error(f"CRITICAL SAFETY ALERT: Fatigue {score:.2f} detected.")
            # Trigger 'Safety Mode' across agents
            await scratchpad.update_state("system_alert", "HIGH_FATIGUE_STOP")
            await scratchpad.update_state("market_action", "BLOCK_NEW_ORDERS")
            return True
        return False

    async def run_loop(self):
        while True:
            # Poll sensor data from scratchpad (written by Android bridge)
            sensors = scratchpad.get_state("realtime_sensors")
            if sensors and len(sensors) > 10:
                await self.monitor_safety(sensors)
                await scratchpad.update_state("realtime_sensors", []) # Clear buffer
            await asyncio.sleep(5)
