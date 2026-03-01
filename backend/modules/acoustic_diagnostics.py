import librosa
import numpy as np
import pyaudio
from loguru import logger
from backend.scratchpad import scratchpad

class AcousticDiagnosticsModule:
    """Detects vehicle health issues via engine sound analysis."""
    
    def __init__(self):
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.chunk = 1024
        
    def analyze_engine_sound(self, audio_data):
        """Perform spectral analysis to detect abnormal engine knocking."""
        # Convert buffer to numpy array
        y = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
        
        # Fundamental frequency extraction
        pitches, magnitudes = librosa.piptrack(y=y, sr=self.rate)
        avg_pitch = np.mean(pitches[pitches > 0]) if any(pitches > 0) else 0
        
        # Check for 'Knocking' (Rapid bursts of high frequency)
        spectral_flatness = librosa.feature.spectral_flatness(y=y)
        if np.mean(spectral_flatness) > 0.05:
            return "WARNING: ENGINE KNOCKING DETECTED"
        return "NORMAL"

    async def run_diagnostics(self):
        p = pyaudio.PyAudio()
        stream = p.open(format=self.format, channels=self.channels, rate=self.rate, 
                        input=True, frames_per_buffer=self.chunk)
        
        logger.info("Acoustic Diagnostics: Sampling engine noise...")
        data = stream.read(self.chunk * 10) # 10 chunks
        result = self.analyze_engine_sound(data)
        
        if "WARNING" in result:
            await scratchpad.update_state("system_alert", "ENGINE_HEALTH_WARNING")
            logger.warning(result)
        
        stream.stop_stream()
        stream.close()
        p.terminate()

    async def run_loop(self):
        while True:
            # Run diagnostics every 4 hours or manually
            await self.run_diagnostics()
            await asyncio.sleep(14400) # 4 hours
