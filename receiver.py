import socket
import json

# Set up a UDP socket (AF_INET = IPv4, SOCK_DGRAM = UDP)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to your local machine on port 5000
sock.bind(('localhost', 5000))
print("Receiver is active and listening on port 5000...")

# Create an infinite loop to keep listening for incoming messages
while True:
    # Wait to receive up to 1024 bytes of data
    data, address = sock.recvfrom(1024)
    
    # Decode the raw bytes back into a Python dictionary (JSON)
    packet = json.loads(data.decode('utf-8'))
    
    print(f"\n--- New Packet from {address} ---")
    print(f"Sequence: {packet['sequence_number']}")
    print(f"Payload: {packet['payload']}")
    print(f"Integrity Hash: {packet['checksum']}")