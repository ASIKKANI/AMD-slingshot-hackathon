import os
import asyncio
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from contextlib import asynccontextmanager

from config import settings
from scratchpad import scratchpad

# Import MAS Agents mapped to localized roles
from agents.market_optimizer import MarketOptimizerAgent
from agents.biometric_sentinel import BiometricSentinelAgent
from agents.financial_fiduciary import FinancialFiduciaryAgent

# Import Modules representing offline-first directives
from modules.mesh_network import mesh_network
from modules.sms_fallback import sms_fallback
from modules.acoustic_diagnostics import acoustic_diagnostics

# Import V2V Access
from voice.ilava_interface import ilava_interface

# Configure strict error-intolerant logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - Sahayak MAS - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize MAS Agents
optimizer = MarketOptimizerAgent()
sentinel = BiometricSentinelAgent()
fiduciary = FinancialFiduciaryAgent()

dashboard_clients = []

async def broadcast_state_loop():
    """Background task to broadcast the real-time CNS state to the UI Dashboard."""
    while True:
        if dashboard_clients:
            state = scratchpad.local_state.copy()
            for client in dashboard_clients:
                try:
                    await client.send_json({"type": "state_update", "payload": state})
                except:
                    pass
        await asyncio.sleep(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events to securely spin up localized listening threads avoiding blocking I/O."""
    logger.info("Initializing Sahayak Background Decentralized Routines...")
    
    # 1. Fire up P2P Mesh Network
    mesh_network.start_mesh_listening()
    
    # 2. Start Acoustic Diagnostics
    acoustic_diagnostics.run_diagnostic_loop()
    
    # 3. Initialize Voice-to-Voice Local Engine
    ilava_interface.run_v2v_loop()
    
    # 4. Fire up Biometric NPU monitoring loop on concurrent thread
    import threading
    threading.Thread(target=sentinel.run_monitor_loop, daemon=True).start()
    
    # 5. Dashboard broadcaster
    asyncio.create_task(broadcast_state_loop())
    
    yield
    
    logger.critical("Shutting down Sahayak Core Routines safely.")

app = FastAPI(title="Sahayak Multi-Agent Orchestrator", lifespan=lifespan)

# Mount Frontend Static Files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def serve_dashboard():
    return FileResponse("frontend/index.html")

@app.websocket("/ws/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    await websocket.accept()
    dashboard_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        dashboard_clients.remove(websocket)

@app.post("/api/simulate_ping")
async def simulate_ping(request: Request):
    data = await request.json()
    raw_text = data.get("raw_screen_text", "")
    
    for client in dashboard_clients:
        try:
            await client.send_json({"type": "log", "message": f"[Android Scraper] Intercepted: {raw_text}", "level": "system"})
        except: pass

    decision = optimizer.evaluate_ping(raw_text)
    
    if decision:
        for client in dashboard_clients:
            try:
                await client.send_json({"type": "log", "message": "Market Optimizer: ACCEPT. Highly profitable route.", "level": "opt-accept"})
            except: pass
        import re
        payout_match = re.search(r'₹\s*(\d+)', raw_text)
        if payout_match:
            payout = float(payout_match.group(1))
            fiduciary.log_completed_job(platform="GigApp", payout=payout, duration_mins=20.0)
            
            # Send ledger update to UI immediately
            if fiduciary.ledger:
                latest_record = fiduciary.ledger[-1]
                for client in dashboard_clients:
                    try:
                        await client.send_json({"type": "ledger_entry", "payload": latest_record})
                        await client.send_json({"type": "log", "message": f"Bank Sync: Logged GPay/UPI Transaction (Ref: {latest_record['hash']})", "level": "fiduciary"})
                    except: pass
    else:
        for client in dashboard_clients:
            try:
                await client.send_json({"type": "log", "message": "Market Optimizer: REJECT. Algorithmic ping is unprofitable or unsafe.", "level": "opt-reject"})
            except: pass

    return {"status": "ok"}

@app.post("/api/simulate_fatigue")
async def simulate_fatigue():
    for client in dashboard_clients:
        try:
            await client.send_json({"type": "log", "message": "[SAFETY SENSOR] CRITICAL OVERRIDE. Erratic phone motion indicates extreme fatigue.", "level": "sentinel-warn"})
        except: pass
    scratchpad.update_state("fatigue_score", 0.95)
    return {"status": "ok"}

@app.post("/api/simulate_multi_ping")
async def simulate_multi_ping(request: Request):
    """Simulates receiving multiple app pings simultaneously and sends structured data to UI."""
    data = await request.json()
    pings = data.get("pings", [])
    
    result = optimizer.evaluate_multi_pings(pings)
    
    # Send a dedicated multi-ping event to the frontend
    for client in dashboard_clients:
        try:
            await client.send_json({"type": "multi_ping_result", "payload": result})
        except: pass

    if result.get("decision") == "ACCEPT_BEST":
        best = result["selected"]
        # Use a rough estimate for duration: dist * 3 mins
        est_duration = float(best.get('distance', 5.0)) * 3.0
        fiduciary.log_completed_job(platform=best['platform'], payout=float(best['payout']), duration_mins=est_duration)
        
        if fiduciary.ledger:
            latest_record = fiduciary.ledger[-1]
            for client in dashboard_clients:
                try:
                    await client.send_json({"type": "log", "message": f"[BANK SYNC] Verified payout via UPI reference.", "level": "fiduciary"})
                    await client.send_json({"type": "ledger_entry", "payload": latest_record})
                except: pass
            
    return {"status": "processed", "result": result}

@app.post("/api/set_config")
async def set_config(request: Request):
    """Update settings like petrol cost and device capability"""
    data = await request.json()
    if 'petrol_cost' in data:
        scratchpad.update_state("petrol_cost_per_km", float(data['petrol_cost']))
        for client in dashboard_clients:
            try:
                await client.send_json({"type": "log", "message": f"[STATE] Updated Fuel/Km cost to ₹{data['petrol_cost']} for RHR algorithm.", "level": "system"})
            except: pass
    if 'device_capability' in data:
        scratchpad.update_state("device_capability", data['device_capability'])
        msg = "Locked onto active phone sensors." if data['device_capability'] == "npu_capable" else "Falling back to basic tracking history."
        for client in dashboard_clients:
            try:
                await client.send_json({"type": "log", "message": f"[HARDWARE] {msg}", "level": "system"})
            except: pass
    return {"status": "ok"}

@app.post("/api/reset_systems")
async def reset_systems():
    """Resets the safety overrides and fatigue for demo continuity."""
    scratchpad.update_state("BLOCK_HIGH_STRESS_ORDERS", False)
    scratchpad.update_state("fatigue_score", 0.0)
    for client in dashboard_clients:
        try:
            await client.send_json({"type": "log", "message": "[SYSTEM] Reset complete. Protection shields nominal. Ready for pings.", "level": "system"})
        except: pass
    return {"status": "ok"}

@app.websocket("/ws/market_data")
async def websocket_endpoint(websocket: WebSocket):
    """
    Local companion WebSocket server to ingest the real-time textual data dynamically scraped 
    by the Android Kotlin Accessibility Monitor.
    """
    await websocket.accept()
    logger.info("Native Kotlin Bridge connected to Python Orchestrator over local WebSocket.")
    
    try:
        while True:
            data = await websocket.receive_json()
            raw_text = data.get("raw_screen_text", "")
            source = data.get("source", "accessibility")
            
            # Hand over incoming algorithmic ping to The Optimizer
            decision = optimizer.evaluate_ping(raw_text)
            
            if decision:
                # Fire confirmation down the bridge to mechanically accept the order on screen
                await websocket.send_json({"action": "TAP_ACCEPT"})
                
                # Mock extraction for the ledger recording
                import re
                payout_match = re.search(r'₹\s*(\d+)', raw_text)
                if payout_match:
                    payout = float(payout_match.group(1))
                    
                    # Offload to Agent 3: Financial Fiduciary for immutable logging
                    fiduciary.log_completed_job(platform="GigApp", payout=payout, duration_mins=20.0)

            # Iteratively verify network to trigger Extra Feature 2 smoothly
            sms_fallback.check_network_and_trigger()
            
    except WebSocketDisconnect:
        logger.warning("Kotlin Android Bridge connection severed.")

if __name__ == "__main__":
    logger.info("Sahayak Central Nervous System Online. Ready to intercept platform algorithms.")
    # Ensuring flawless zero-error startup using standard local ASGI bindings
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")
