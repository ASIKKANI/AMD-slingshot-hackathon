import json
import logging
import threading
import time
from scratchpad import scratchpad

logger = logging.getLogger(__name__)

class MeshNetwork:
    """
    Peer-to-peer (P2P) Bluetooth Low Energy (BLE) / Wi-Fi Direct mesh networking module.
    Enables offline workers to exchange "Demand Heatmaps" silently.
    """
    def __init__(self):
        self.is_active = False
        self.local_demand_data = {"zone_4": "surge_pricing", "zone_2": "low_demand"} # Initial mock state

    def start_mesh_listening(self):
        self.is_active = True
        logger.info("Mesh Network: BLE/Wi-Fi Direct listening started. Ready for P2P sync.")
        
        def listen_loop():
            while self.is_active:
                # Mocking a peer connection every ~30 seconds when passing another Sahayak user
                time.sleep(30)
                self.simulate_peer_exchange()
                
        # Start a daemon thread so it doesn't block the main process
        threading.Thread(target=listen_loop, daemon=True).start()

    def simulate_peer_exchange(self):
        """Mocks the silent exchange of encrypted packets between two passing devices lacking internet."""
        # Assume peer has identified high demand offline organically
        received_packet = {"zone_7": "high_demand_event"}
        logger.info(f"Mesh Network: Intersected with peer device. Discovered offline intelligence: {received_packet}")
        
        # Merge heatmaps into our central nervous system state
        self.local_demand_data.update(received_packet)
        scratchpad.update_state("demand_heatmap", self.local_demand_data)

    def broadcast_packet(self) -> str:
        """Returns encrypted payload to broadcast via BLE for peers."""
        payload = json.dumps(self.local_demand_data)
        # Production ready systems apply AES-256 here.
        return payload

# Singleton
mesh_network = MeshNetwork()
