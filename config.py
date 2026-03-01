import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # System Preferences & MAS Constants
    CRITICAL_FATIGUE_THRESHOLD: float = 0.8  # Safety overriding value threshold
    MIN_PROFIT_MARGIN: float = 0.15          # Minimum acceptable gig profit margin
    MAX_WAIT_TIME_MINUTES: int = 15          # Maximum acceptable wait time before fallback

    # Hardware & Edge Inference Flags (AMD Synergies)
    USE_AMD_RYZEN_NPU: bool = True
    ROCM_ENABLED: bool = bool(int(os.getenv("ROCM_ENABLED", "0")))
    ILAVA_RVQ_ITERATIONS: int = 16           # Reduced down from 32 for lower latency
    ILAVA_REAL_TIME_FACTOR: float = 0.480    # Target sub-200ms conversational latency

    # External APIs (Twilio for SMS Fallback)
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "dummy_sid")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "dummy_token")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "+1234567890")

    # DB & State Management Constants
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    DB_URL: str = os.getenv("DB_URL", "sqlite:///./local_ledger.db")

settings = Settings()
