import socket
import json
import time
import hashlib

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# The listening ports for our two intermediate routers
path_ports = [5001, 5002]

# Send 6 packets in a loop
for i in range(1, 7):
    payload_text = f"This is packet {i}"
    current_time = time.time()
    
    hash_input = f"{payload_text}{current_time}".encode('utf-8')
    packet_hash = hashlib.sha256(hash_input).hexdigest()

    packet = {
        "sequence_number": i,
        "source_address": "localhost",
        "destination_address": "localhost:5000",
        "payload": payload_text,
        "timestamp": current_time,
        "checksum": packet_hash
    }

    message_bytes = json.dumps(packet).encode('utf-8')

    # Packet Spraying: alternate between Path 1 (index 0) and Path 2 (index 1)
    target_port = path_ports[i % 2]
    
    sock.sendto(message_bytes, ('localhost', target_port))
    print(f"Sent Sequence {i} via Router on port {target_port}")
    
    # Slight delay to simulate realistic network spacing
    time.sleep(0.5)