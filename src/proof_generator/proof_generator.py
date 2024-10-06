import asyncio
import hashlib
import os
from dataclasses import dataclass
from typing import List

from .timekeeping import TimekeepingUnit
from .secure_element import SecureElement

@dataclass
class TimeProof:
    node_id: str
    gps_data: 'GpsData'
    local_time: float
    oscillator_offset: float
    previous_proof_hash: str
    nonce: str
    signature: str

class ProofGenerator:
    def __init__(self, timekeeping_unit: TimekeepingUnit, secure_element: SecureElement):
        self.timekeeping_unit = timekeeping_unit
        self.secure_element = secure_element
        self.last_proof_hash = '0' * 64
        self.proof_interval = 60  # 1 minute

    async def run(self):
        while True:
            await self.generate_and_store_proof()
            await asyncio.sleep(self.proof_interval)

    async def generate_proof(self) -> TimeProof:
        gps_data = await self.timekeeping_unit.gps_module.get_time_data()
        local_time = self.timekeeping_unit.get_current_time()
        oscillator_offset = self.timekeeping_unit.oscillator.offset
        nonce = os.urandom(32).hex()

        proof = TimeProof(
            node_id=self.secure_element.node_id,
            gps_data=gps_data,
            local_time=local_time,
            oscillator_offset=oscillator_offset,
            previous_proof_hash=self.last_proof_hash,
            nonce=nonce,
            signature=''
        )

        proof_hash = hashlib.sha3_256(str(proof).encode()).hexdigest()
        proof.signature = self.secure_element.sign(proof_hash)

        return proof

    async def generate_and_store_proof(self):
        proof = await self.generate_proof()
        self.last_proof_hash = hashlib.sha3_256(str(proof).encode()).hexdigest()
        return proof
