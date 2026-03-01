import asyncio
from loguru import logger
from backend.scratchpad import scratchpad
from backend.config import config

class MarketIntelligenceAgent:
    """Calculates Real Hourly Rate (RHR) and optimizes gig acceptance."""
    
    def calculate_rhr(self, payout, distance_km, estimated_time_hr):
        costs = (config.FUEL_COST_PER_KM + config.VEHICLE_DEPRECIATION_PER_KM) * distance_km
        net_profit = payout - costs
        rhr = net_profit / estimated_time_hr
        return rhr

    async def analyze_ping(self, ping_data: dict):
        payout = ping_data.get("payout", 0.0)
        dist = ping_data.get("distance", 0.0)
        time_est = ping_data.get("estimated_time", 0.5)

        rhr = self.calculate_rhr(payout, dist, time_est)
        logger.info(f"Incoming Ping: RHR = ₹{rhr:.2f}/hr | Target = ₹{config.MIN_RHR_TARGET}/hr")

        if rhr >= config.MIN_RHR_TARGET:
            success = await scratchpad.update_state("market_action", "ACCEPT_ORDER")
            if success:
                logger.success(f"PROFITABLE ORDER ACCEPTED: RHR ₹{rhr:.2f}")
                return True
        else:
            logger.info("SKIP ORDER: RHR below threshold.")
        return False

    async def run_loop(self):
        while True:
            ping_data = scratchpad.get_state("active_pings")
            if ping_data:
                await self.analyze_ping(ping_data)
                await scratchpad.update_state("active_pings", None) # Clear processed ping
            await asyncio.sleep(1)
