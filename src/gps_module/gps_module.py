import asyncio
import random
from dataclasses import dataclass

@dataclass
class GpsData:
    gps_week: int
    gps_seconds: float
    satellite_prns: List[int]
    signal_strengths: List[float]

class GpsModule:
    def __init__(self, port: str):
        self.port = port

    async def get_time_data(self) -> GpsData:
        # In a real implementation, this would interface with actual GPS hardware
        await asyncio.sleep(0.1)  # Simulate GPS data acquisition time
        return GpsData(
            gps_week=random.randint(2000, 3000),
            gps_seconds=random.uniform(0, 604800),
            satellite_prns=[random.randint(1, 32) for _ in range(4)],
            signal_strengths=[random.uniform(30, 50) for _ in range(4)]
        )
