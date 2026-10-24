import socket
import json
import time
import hashlib

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('localhost', 4000))
sock.settimeout(2.0)

# The Adaptive Engine: Track the health and latency of our paths[cite: 4]
paths = {
    5001: {"status": "healthy", "latency": 0.0},
    5002: {"status": "healthy", "latency": 0.0}
}

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
    
    # Adaptive Selection: Only distribute packets across currently healthy paths[cite: 4]
    healthy_ports = [port for port, data in paths.items() if data["status"] == "healthy"]
    
    if not healthy_ports:
        print("CRITICAL: All paths are down! Network failure.")
        break
        
    # Spray packets based on the remaining healthy ports
    target_port = healthy_ports[i % len(healthy_ports)]
    
    while True:
        sock.sendto(message_bytes, ('localhost', target_port))
        print(f"Sent Sequence {i} via Router on port {target_port}")
        
        try:
            ack_data, _ = sock.recvfrom(1024)
            ack_json = json.loads(ack_data.decode('utf-8'))
            
            if ack_json.get("type") == "ACK" and ack_json.get("ack_sequence") == i:
                # Calculate the round-trip latency in milliseconds[cite: 4]
                rtt_ms = (time.time() - current_time) * 1000
                paths[target_port]["latency"] = round(rtt_ms, 2)
                
                print(f"--> Success: ACK for seq {i} | Latency: {paths[target_port]['latency']}ms\n")
                break 
                
        except (socket.timeout, ConnectionResetError):
            # Failure Detection: Mark the path as failed and stop using it[cite: 4]
            print(f"*** FAILURE DETECTED: Router {target_port} is dead. Rerouting... ***")
            paths[target_port]["status"] = "failed"
            
            # Find a new healthy path to reroute this packet[cite: 4]
            healthy_ports = [port for port, data in paths.items() if data["status"] == "healthy"]
            if not healthy_ports:
                print("CRITICAL: All paths are down! Network failure.")
                break
                
            target_port = healthy_ports[0] # Reroute to the surviving path
            
    time.sleep(0.5)