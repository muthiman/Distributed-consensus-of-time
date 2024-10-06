import asyncio
from .gps_module import GpsModule
from .oscillator import HighPrecisionOscillator

class TimekeepingUnit:
    def __init__(self, gps_module: GpsModule, oscillator: HighPrecisionOscillator):
        self.gps_module = gps_module
        self.oscillator = oscillator
        self.last_sync = 0
        self.sync_interval = 900  # 15 minutes

    async def run(self):
        while True:
            await self.synchronize()
            await asyncio.sleep(self.sync_interval)

    async def synchronize(self):
        gps_data = await self.gps_module.get_time_data()
        gps_time = gps_data.gps_week * 604800 + gps_data.gps_seconds
        local_time = self.oscillator.get_time()
        offset = gps_time - local_time
        self.oscillator.set_offset(offset)
        self.last_sync = local_time

    def get_current_time(self) -> float:
        return self.oscillator.get_time()

    def is_within_acceptable_range(self, timestamp: float, reference: float, tolerance: float = 0.005) -> bool:
        return abs(timestamp - reference) <= tolerance
