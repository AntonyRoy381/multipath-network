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
    
    print(f"[Network] Received sequence {seq}")
    
    # 1. Immediately send an ACK back to the sender[cite: 4]
    ack_packet = {
        "type": "ACK",
        "ack_sequence": seq
    }
    # Send directly to the sender's bound port (4000)
    sock.sendto(json.dumps(ack_packet).encode('utf-8'), ('localhost', 4000))
    print(f"[Network] Sent ACK for sequence {seq}")
    
    # 2. Process the packet for application delivery
    packet_buffer[seq] = packet
    
    while expected_sequence in packet_buffer:
        delivered_packet = packet_buffer.pop(expected_sequence)
        print(f">>> [App] Delivered: Seq {expected_sequence} - '{delivered_packet['payload']}'\n")
        expected_sequence += 1