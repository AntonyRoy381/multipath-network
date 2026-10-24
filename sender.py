import socket
import json
import time
import hashlib

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('localhost', 4000))
sock.settimeout(2.0)

path_ports = [5001, 5002]

for i in range(1, 50):
    payload_text = f"This is packet {i}"
    current_time = time.time()
    hash_input = f"{payload_text}{current_time}".encode('utf-8')
    packet_hash = hashlib.sha256(hash_input).hexdigest()

    packet = {
        "sequence_number": i,
        "source_address": "localhost:4000",
        "destination_address": "localhost:5000",
        "payload": payload_text,
        "timestamp": current_time,
        "checksum": packet_hash
    }
    
    message_bytes = json.dumps(packet).encode('utf-8')
    target_port = path_ports[i % 2]
    
    while True:
        sock.sendto(message_bytes, ('localhost', target_port))
        print(f"Sent Sequence {i} via Router on port {target_port}")
        
        try:
            ack_data, _ = sock.recvfrom(1024)
            ack_json = json.loads(ack_data.decode('utf-8'))
            
            if ack_json.get("type") == "ACK" and ack_json.get("ack_sequence") == i:
                print(f"--> Success: Received ACK for sequence {i}\n")
                break 
                
        except socket.timeout:
            print(f"*** TIMEOUT: No ACK for sequence {i}. Retransmitting... ***")
        except ConnectionResetError:
            # Catch the Windows 10054 error when the router is dead
            print(f"*** ROUTER DEAD: Windows rejected packet at port {target_port}. Retransmitting... ***")
            time.sleep(1) # Prevent the console from spamming too fast
            
    time.sleep(0.5)