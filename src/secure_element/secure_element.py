import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ed25519

class SecureElement:
    def __init__(self):
        self.node_id = os.urandom(32).hex()
        self.private_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()

    def sign(self, data: str) -> str:
        signature = self.private_key.sign(data.encode())
        return signature.hex()

    def verify(self, data: str, signature: str) -> bool:
        try:
            self.public_key.verify(bytes.fromhex(signature), data.encode())
            return True
        except:
            return False
