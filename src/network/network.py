import asyncio
import aiohttp
from typing import List, Dict
from .proof_generator import TimeProof

class NetworkInterface:
    def __init__(self, p2p_port: int, da_layer_url: str):
        self.p2p_port = p2p_port
        self.da_layer_url = da_layer_url
        self.peers: List[str] = []

    async def run(self):
        await asyncio.gather(
            self.listen_for_connections(),
            self.discover_peers()
        )

    async def listen_for_connections(self):
        server = await asyncio.start_server(self.handle_connection, '0.0.0.0', self.p2p_port)
        async with server:
            await server.serve_forever()

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = await reader.read(1024)
        message = data.decode()
        # Handle incoming messages (e.g., time requests, proofs)
        writer.close()

    async def discover_peers(self):
        # Implement peer discovery logic
        pass

    async def submit_proof(self, proof: TimeProof):
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.da_layer_url}/submit_proof", json=proof.to_dict()) as response:
                return await response.json()

    async def get_recent_proofs(self) -> List[Dict]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.da_layer_url}/get_recent_proofs") as response:
                return await response.json()
