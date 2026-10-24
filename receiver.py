import socket
import json

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('localhost', 5000))
print("Receiver listening on port 5000...")

expected_sequence = 1
packet_buffer = {}

while True:
    data, address = sock.recvfrom(1024)
    packet = json.loads(data.decode('utf-8'))
    seq = packet['sequence_number']
    
    print(f"[Network Layer] Received sequence {seq} from router at {address}")
    
    # Store the out-of-order packet in the buffer dictionary
    packet_buffer[seq] = packet
    
    # Check if the buffer contains the next sequence number we need to deliver[cite: 4]
    while expected_sequence in packet_buffer:
        delivered_packet = packet_buffer.pop(expected_sequence)
        print(f">>> [App Layer] Delivered: Sequence {expected_sequence} - '{delivered_packet['payload']}'")
        expected_sequence += 1