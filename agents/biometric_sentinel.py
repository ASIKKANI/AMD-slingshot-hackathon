import random
import time
from scratchpad import scratchpad
from config import settings
import logging

logger = logging.getLogger(__name__)

class BiometricSentinelAgent:
    """
    Monitors localized sensor data to detect driver fatigue and erratic driving, triggering safety overrides.
    Designed to work with standard smartphone accelerometers and gyroscopes.
    """
    def __init__(self):
        self.is_monitoring = False
        
    def poll_sensors(self) -> float:
        """Simulate polling the Android accelerometer/gyro bridge data."""
        # Simulate noisy data stream corresponding to harsh braking and G-force impacts
        accelerometer_variance = random.uniform(0.1, 2.5) 
        return accelerometer_variance

    def infer_fatigue(self, sensor_data: float) -> float:
        """
        Mock NPU Anomaly Detection vs Cloud Heuristic fallback. 
        In production, npu_capable means quantified INT8 neural network evaluated locally.
        """
        device_cap = scratchpad.get_state("device_capability")
        
        if device_cap == "npu_capable":
            # High fidelity NPU analysis
            stress = min((sensor_data / 2.5), 1.0)
            if stress > 0.8:
                logger.warning("[NPU Edge Inference] Critical fatigue pattern detected locally. Latency: 8ms")
        else:
            # Fallback for old phones without dedicated ML silicon
            logger.debug("Cloud/Heuristic Fallback: No NPU detected. Using basic rules engine.")
            # Heuristics are less accurate and slower
            stress = min((sensor_data / 3.0), 1.0) 
            if stress > 0.8:
                logger.warning("[Heuristic Fallback] High continuous active time detected. Triggering warning.")
                
        return stress
        
    def run_monitor_loop(self):
        """Infinite loop simulating device-local checking of physical condition."""
        self.is_monitoring = True
        logger.info("[SENSOR ACTIVE] Activity Tracker analyzing real-time rider motion.")
        
        while self.is_monitoring:
            data = self.poll_sensors()
            fatigue = self.infer_fatigue(data)
            
            # Update scratchpad - safety thresholds are evaluated inherently inside Scratchpad.update_state
            scratchpad.update_state("fatigue_score", fatigue)
            time.sleep(5) # Polling cycle - batched to limit battery usage
