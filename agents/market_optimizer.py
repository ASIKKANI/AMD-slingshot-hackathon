import re
from typing import Dict, Any
from scratchpad import scratchpad
from config import settings
import logging

logger = logging.getLogger(__name__)

class MarketOptimizerAgent:
    """
    Maximizes worker profit by calculating the Real Hourly Rate (RHR) across incoming pings.
    Rejects loss-making algorithmic assignments.
    """
    def __init__(self):
        self.active_pings = []
    
    def calculate_rhr(self, payout: float, time_active: float, time_idle: float, distance_km: float) -> float:
        """
        Calculates the Real Hourly Rate (RHR).
        RHR = (Sum(Payouts) - Costs) / (Time_Active + Time_Idle)
        Assumed costs per km: Dynamic Fuel cost from user + Depreciation
        """
        petrol_cost = scratchpad.get_state("petrol_cost_per_km") or 2.5
        costs = distance_km * (petrol_cost + 1.0) # Fuel + wear and tear
        total_time_hours = (time_active + time_idle) / 60.0
        if total_time_hours <= 0:
            return 0.0
        
        rhr = (payout - costs) / total_time_hours
        return rhr

    def parse_ping(self, raw_text: str, platform: str) -> Dict[str, Any]:
        """Extracts stats and RHR from a given ping text."""
        try:
            payout_match = re.search(r'₹\s*(\d+)', raw_text)
            distance_match = re.search(r'(\d+\.?\d*)\s*km', raw_text.lower())
            
            if not payout_match or not distance_match:
                return None
                
            payout = float(payout_match.group(1))
            distance = float(distance_match.group(1))
            
            time_active = distance * 3.0 # Assume 3 mins per km in city traffic
            time_idle = 5.0 # Average idle time waiting
            
            rhr = self.calculate_rhr(payout, time_active, time_idle, distance)
            return {"platform": platform, "payout": payout, "distance": distance, "rhr": rhr, "raw": raw_text}
        except: return None

    def evaluate_multi_pings(self, pings: list) -> Dict[str, Any]:
        """
        Takes a list of ping texts from multiple platforms intercepted at the same time.
        Parses them, compares RHR, and returns the strictly most profitable one.
        """
        # Check Safety Override from Biometric Sentinel
        if scratchpad.get_state("BLOCK_HIGH_STRESS_ORDERS"):
            logger.warning("Market Optimizer: Blocking all assignments. Safety Override is active.")
            return {"decision": "REJECT_ALL", "reason": "Fatigue Block Active"}
            
        parsed_pings = []
        for p in pings:
            parsed = self.parse_ping(p['text'], p['platform'])
            if parsed: parsed_pings.append(parsed)
            
        if not parsed_pings:
            return {"decision": "NONE_VALID"}
            
        # Sort by best RHR
        parsed_pings.sort(key=lambda x: x['rhr'], reverse=True)
        best_ping = parsed_pings[0]
        
        target_rhr = 150 * (1 + settings.MIN_PROFIT_MARGIN)
        
        if best_ping['rhr'] > target_rhr:
            logger.info(f"Cross-Platform Best: {best_ping['platform']} at ₹{best_ping['payout']} (RHR: {best_ping['rhr']:.1f})")
            return {"decision": "ACCEPT_BEST", "selected": best_ping, "all_parsed": parsed_pings}
        else:
            return {"decision": "REJECT_ALL", "reason": "All pings below target RHR", "all_parsed": parsed_pings}

    def evaluate_ping(self, raw_text: str) -> bool:
        """Legacy single ping evaluation, kept for backwards compatibility."""
        """Parse text to extract fare and distance, and decide whether to accept."""
        # Check Safety Override from Biometric Sentinel
        if scratchpad.get_state("BLOCK_HIGH_STRESS_ORDERS"):
            logger.warning("Market Optimizer: Blocking assignment. Safety Override (Fatigue/Stress) is active.")
            return False

        # Primitive extraction logic based on raw OCR text
        try:
            payout_match = re.search(r'₹\s*(\d+)', raw_text)
            distance_match = re.search(r'(\d+\.?\d*)\s*km', raw_text.lower())
            
            if not payout_match or not distance_match:
                return False
                
            payout = float(payout_match.group(1))
            distance = float(distance_match.group(1))
            
            # Assumptions for RHR calc for a single ping
            time_active = distance * 3.0 # Assume 3 mins per km in city traffic
            time_idle = 5.0 # Average idle time waiting for ping
            
            rhr = self.calculate_rhr(payout, time_active, time_idle, distance)
            
            logger.info(f"Analyzed Ping - Payout: ₹{payout}, Dist: {distance}km -> RHR: {rhr:.2f} INR/hr")
            
            # Acceptance threshold logic based on margin
            target_rhr = 150 * (1 + settings.MIN_PROFIT_MARGIN) # Target minimum
            if rhr > target_rhr:
                logger.info(f"Decision: ACCEPT. Profitable route identified (+{(rhr-target_rhr):.2f} over minimum).")
                return True
            else:
                logger.info("Decision: REJECT. Algorithmic ping is unprofitable.")
                return False
                
        except Exception as e:
            logger.error(f"Error formulating RHR: {e}")
            return False
