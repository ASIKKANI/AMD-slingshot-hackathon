import asyncio
import signal
from loguru import logger
from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

# Import Agents and Modules
from backend.scratchpad import scratchpad
from backend.agents.market_optimizer import MarketIntelligenceAgent
from backend.agents.biometric_sentinel import BiometricSentinel
from backend.agents.financial_fiduciary import FinancialFiduciary
from backend.modules.mesh_network import MeshNetworkModule
from backend.modules.sms_fallback import SmsFallbackModule
from backend.modules.acoustic_diagnostics import AcousticDiagnosticsModule
from backend.voice.ilava_interface import IlavaVoiceInterface

app = FastAPI(title="Project Sahayak Core")

# Global Agent Instances
market_agent = MarketIntelligenceAgent()
biometric_agent = BiometricSentinel()
financial_fiduciary = FinancialFiduciary()
mesh_module = MeshNetworkModule()
sms_fallback = SmsFallbackModule()
acoustic_module = AcousticDiagnosticsModule()
voice_interface = IlavaVoiceInterface()

@app.websocket("/ws/scraper")
async def websocket_scraper(websocket: WebSocket):
    """
    WebSocket endpoint for the Android Accessibility Scraper.
    Receives real-time UI data from gig apps.
    """
    await websocket.accept()
    logger.info("Android Scraper Connected via WebSocket")
    try:
        while True:
            data = await websocket.receive_text()
            # Feed raw text into the Scratchpad for the Market Agent to analyze
            await scratchpad.update_state("active_pings", data)
            logger.debug(f"Received Scraper Data: {data[:50]}...")
    except WebSocketDisconnect:
        logger.warning("Android Scraper Disconnected")

async def run_sahayak_manager():
    """Starts all agent and module loops concurrently."""
    logger.info("Initializing Sahayak Multi-Agent System (MAS)...")
    
    # Registering background tasks
    tasks = [
        asyncio.create_task(market_agent.run_loop()),
        asyncio.create_task(biometric_agent.run_loop()),
        asyncio.create_task(mesh_module.run_loop()),
        asyncio.create_task(sms_fallback.run_loop()),
        asyncio.create_task(acoustic_module.run_loop()),
        asyncio.create_task(voice_interface.run_loop())
    ]
    
    # Wait for all tasks to run indefinitely
    await asyncio.gather(*tasks)

@app.on_event("startup")
async def startup_event():
    # Start the MAS logic in the background when FastAPI starts
    asyncio.create_task(run_sahayak_manager())

if __name__ == "__main__":
    import uvicorn
    # In a real setup, we'd use 'uvicorn main:app --host 0.0.0.0'
    uvicorn.run(app, host="0.0.0.0", port=8000)
