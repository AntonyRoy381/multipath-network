import socket
import json
import time
import hashlib

# Set up the UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Define the message payload and capture the exact current time
payload_text = "Hello! This is test packet number 1."
current_time = time.time()

# Generate a checksum/hash to verify data integrity
# We combine the payload and time, then scramble it into a unique SHA-256 string
hash_input = f"{payload_text}{current_time}".encode('utf-8')
packet_hash = hashlib.sha256(hash_input).hexdigest()

# Construct the exact packet structure required for the project
packet = {
    "sequence_number": 1,
    "source_address": "localhost",
    "destination_address": "localhost:5000",
    "payload": payload_text,
    "timestamp": current_time,
    "checksum": packet_hash
}

# Convert the Python dictionary into a JSON string, then encode it to raw bytes
message_bytes = json.dumps(packet).encode('utf-8')

# Send the bytes to the receiver listening on localhost port 5000
sock.sendto(message_bytes, ('localhost', 5000))
print("Packet successfully sent to the receiver!")