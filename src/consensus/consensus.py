import asyncio
from typing import List, Dict
from .network import NetworkInterface
from .proof_generator import TimeProof

class ConsensusEngine:
    def __init__(self, network: NetworkInterface):
        self.network = network

    async def run(self):
        while True:
            await self.reach_consensus()
            await asyncio.sleep(60)  # Run consensus every minute

    async def reach_consensus(self) -> float:
        proofs = await self.network.get_recent_proofs()
        valid_proofs = self.filter_valid_proofs(proofs)
        return self.calculate_median_time(valid_proofs)

    def filter_valid_proofs(self, proofs: List[Dict]) -> List[TimeProof]:
        # Implement proof validation logic
        return [TimeProof(**proof) for proof in proofs]  # Simplified for brevity

    def calculate_median_time(self, proofs: List[TimeProof]) -> float:
        times = sorted(proof.local_time for proof in proofs)
        mid = len(times) // 2
        return (times[mid] + times[~mid]) / 2

    async def get_consensus_time(self) -> float:
        return await self.reach_consensus()
