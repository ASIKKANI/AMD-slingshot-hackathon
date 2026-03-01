import os
from pydantic_settings import BaseSettings

class SahayakConfig(BaseSettings):
    # System Constants
    PROJECT_NAME: str = "Sahayak"
    LOG_LEVEL: str = "INFO"
    
    # RHR Calculation Constants (Real Hourly Rate)
    FUEL_COST_PER_KM: float = 2.50  # ₹ INR
    VEHICLE_DEPRECIATION_PER_KM: float = 0.75  # ₹ INR
    MIN_RHR_TARGET: float = 150.0  # Minimum target ₹/hour
    
    # Biometric Sentinel Thresholds
    FATIGUE_CRITICAL_THRESHOLD: float = 0.85 
    ERRATIC_DRIVING_WINDOW_SEC: int = 300
    SAFETY_INTERVENTION_TIMEOUT: int = 15 * 60 # 15 minutes forced break
    
    # AI Engine Optimization
    AMD_ROCM_ENABLED: bool = True
    ONNX_NPU_EXECUTION: bool = True
    VOICE_RVQ_ITERATIONS: int = 16 # Optimized for RTF 0.480x
    
    # Redis/Scratchpad
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = 6379
    
    # P2P Mesh Settings
    MESH_SYNC_INTERVAL: int = 60 # seconds
    BLE_SERVICE_UUID: str = "5a41-3a0c-4217-91f1-325d7e4860b7"

    class Config:
        case_sensitive = True

config = SahayakConfig()
