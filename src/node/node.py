import asyncio
from dataclasses import dataclass
from typing import List, Optional

from .gps_module import GpsModule
from .oscillator import HighPrecisionOscillator
from .timekeeping import TimekeepingUnit
from .proof_generator import ProofGenerator
from .network import NetworkInterface
from .secure_element import SecureElement
from .consensus import ConsensusEngine

@dataclass
class NodeConfig:
    node_id: str
    gps_port: str
    p2p_port: int
    da_layer_url: str

class Node:
    def __init__(self, config: NodeConfig):
        self.config = config
        self.gps_module = GpsModule(config.gps_port)
        self.oscillator = HighPrecisionOscillator()
        self.timekeeping_unit = TimekeepingUnit(self.gps_module, self.oscillator)
        self.secure_element = SecureElement()
        self.proof_generator = ProofGenerator(self.timekeeping_unit, self.secure_element)
        self.network = NetworkInterface(config.p2p_port, config.da_layer_url)
        self.consensus_engine = ConsensusEngine(self.network)

    async def run(self):
        await asyncio.gather(
            self.timekeeping_unit.run(),
            self.proof_generator.run(),
            self.network.run(),
            self.consensus_engine.run()
        )

    async def generate_and_submit_proof(self):
        proof = await self.proof_generator.generate_proof()
        await self.network.submit_proof(proof)

    async def validate_action(self, action):
        consensus_time = await self.consensus_engine.get_consensus_time()
        return self.timekeeping_unit.is_within_acceptable_range(action.timestamp, consensus_time)
