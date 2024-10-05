import time
import random
import threading
from datetime import datetime, timedelta
import socket
import json
import sys
import hashlib
import hmac
import statistics

class AdvancedZKClockClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.physical_clock = time.time()
        self.logical_clock = 0
        self.hlc = (self.physical_clock, 0, f"{host}:{port}")
        self.peers = set()
        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_sock.bind((host, port))
        self.lock = threading.Lock()
        self.message_ids = set()
        self.secret_key = self.generate_secret_key()
        self.time_window = []
        self.fault_tolerance = 1  # Adjust based on expected number of faulty nodes
        self.uncertainty_window = 0.01  # 10ms uncertainty
        self.peer_latencies = {}  # Store estimated latencies for each peer

    def generate_secret_key(self):
        return hashlib.sha256(f"{self.host}:{self.port}".encode()).hexdigest()

    def create_signed_message(self, message_type, payload):
        message = {
            "type": message_type,
            "sender": f"{self.host}:{self.port}",
            "hlc": self.hlc,
            "payload": payload,
            "timestamp": time.time()
        }
        message_str = json.dumps(message, sort_keys=True)
        signature = hmac.new(self.secret_key.encode(), message_str.encode(), hashlib.sha256).hexdigest()
        message["signature"] = signature
        return json.dumps(message)

    def verify_message(self, message):
        signature = message.pop("signature", None)
        if not signature:
            return False
        message_str = json.dumps(message, sort_keys=True)
        expected_signature = hmac.new(self.secret_key.encode(), message_str.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, expected_signature)

    def update_hlc(self, received_hlc):
        with self.lock:
            local_physical = time.time()
            msg_physical, msg_logical, _ = received_hlc
            if local_physical > msg_physical:
                self.hlc = (local_physical, 0, f"{self.host}:{self.port}")
            elif local_physical == msg_physical:
                self.hlc = (local_physical, max(self.hlc[1], msg_logical) + 1, f"{self.host}:{self.port}")
            else:
                self.hlc = (msg_physical, msg_logical + 1, f"{self.host}:{self.port}")

    def gossip_time(self):
        for peer in self.peers:
            self.send_time_request(peer)

    def send_time_request(self, peer):
        request = self.create_signed_message("time_request", {
            "t1": time.time()
        })
        self.send_sock.sendto(request.encode(), peer)

    def handle_time_request(self, message, addr):
        t1 = message["payload"]["t1"]
        t2 = time.time()
        response = self.create_signed_message("time_response", {
            "t1": t1,
            "t2": t2,
            "t3": time.time(),
            "physical_clock": self.physical_clock,
            "logical_clock": self.logical_clock,
            "hlc": self.hlc
        })
        self.send_sock.sendto(response.encode(), addr)

    def handle_time_response(self, message, addr):
        t4 = time.time()
        t1 = message["payload"]["t1"]
        t2 = message["payload"]["t2"]
        t3 = message["payload"]["t3"]
        
        # Calculate round-trip time and offset
        rtt = (t4 - t1) - (t3 - t2)
        offset = ((t2 - t1) + (t3 - t4)) / 2

        # Update peer latency estimate
        self.peer_latencies[addr] = rtt / 2

        # Adjust received time for latency
        adjusted_time = message["payload"]["physical_clock"] + offset + (rtt / 2)

        self.time_window.append((adjusted_time, addr))
        if len(self.time_window) > 2 * self.fault_tolerance + 1:
            self.time_window.pop(0)

        self.update_local_time()
        self.update_hlc(tuple(message["payload"]["hlc"]))

    def update_local_time(self):
        if len(self.time_window) >= 2 * self.fault_tolerance + 1:
            sorted_times = sorted(self.time_window, key=lambda x: x[0])
            median_time = sorted_times[len(sorted_times) // 2][0]
            
            # Calculate the weighted average of median and local time
            weight = 0.8  # Adjust this weight based on trust in local clock vs network
            self.physical_clock = (weight * self.physical_clock) + ((1 - weight) * median_time)
            
            self.logical_clock += 1
            self.hlc = (self.physical_clock, self.logical_clock, f"{self.host}:{self.port}")

    def get_current_time(self):
        with self.lock:
            lower_bound = max(self.physical_clock, self.hlc[0]) - self.uncertainty_window
            upper_bound = max(self.physical_clock, self.hlc[0]) + self.uncertainty_window
            return (lower_bound, upper_bound)

    def receive_messages(self):
        while True:
            data, addr = self.recv_sock.recvfrom(1024)
            message = json.loads(data.decode())
            if self.verify_message(message):
                self.handle_message(message, addr)
            else:
                print(f"Received invalid message from {addr}")

    def handle_message(self, message, addr):
        if message["type"] == "time_request":
            self.handle_time_request(message, addr)
        elif message["type"] == "time_response":
            self.handle_time_response(message, addr)
        elif message["type"] == "join":
            self.handle_join_message(addr)

    def handle_join_message(self, addr):
        self.peers.add(addr)
        print(f"New peer joined: {addr[0]}:{addr[1]}")

    def join_network(self, known_peer):
        if known_peer:
            message = self.create_signed_message("join", {})
            self.send_sock.sendto(message.encode(), known_peer)
            self.peers.add(known_peer)

    def run(self):
        threading.Thread(target=self.receive_messages, daemon=True).start()
        while True:
            self.gossip_time()
            time.sleep(1)

def run_client(host, port, known_peer=None):
    client = AdvancedZKClockClient(host, port)
    if known_peer:
        client.join_network(known_peer)
    client.run()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <host> <port> [<known_peer_host:port>]")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    known_peer = None
    if len(sys.argv) > 3:
        known_peer = tuple(sys.argv[3].split(':'))
        known_peer = (known_peer[0], int(known_peer[1]))

    run_client(host, port, known_peer)
