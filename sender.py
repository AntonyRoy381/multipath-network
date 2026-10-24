import socket
import json
import time
import hashlib
import random

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('localhost', 4000))
sock.settimeout(2.0)

# The Adaptive Engine: Now tracking latency and a dynamic score[cite: 4]
paths = {
    5001: {"status": "healthy", "latency": 1.0, "score": 0},
    5002: {"status": "healthy", "latency": 1.0, "score": 0}
}

# Define the weights for the scoring formula[cite: 4]
W1_LATENCY = 1.0
W2_LOSS = 10.0
W3_CONGESTION = 1.0
W4_HOP = 1.0

def update_scores():
    """Computes a score for each healthy path using the weighted formula[cite: 4]."""
    for port, data in paths.items():
        if data["status"] == "healthy":
            # Score = w1*(latency) + w2*(loss) + w3*(congestion) + w4*(hop count)[cite: 4]
            # Assuming loss=0 and hop=1 for currently healthy paths in this lab scenario
            data["score"] = round((W1_LATENCY * data["latency"]) + (W4_HOP * 1), 2)

def select_best_path():
    """Assigns more traffic to better-performing paths (lower scores)[cite: 4]."""
    healthy_ports = [p for p, d in paths.items() if d["status"] == "healthy"]
    
    if not healthy_ports:
        return None
    if len(healthy_ports) == 1:
        return healthy_ports[0]
        
    # Get the scores for Path 1 and Path 2
    score1 = paths[healthy_ports[0]]["score"]
    score2 = paths[healthy_ports[1]]["score"]
    total_score = score1 + score2
    
    # Invert the probability: If Path 1 has a low score, it gets a high probability
    prob_path_1 = score2 / total_score if total_score > 0 else 0.5
    
    # Randomly select a path based on the weighted probability
    if random.random() < prob_path_1:
        return healthy_ports[0]
    else:
        return healthy_ports[1]

for i in range(1, 100):
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
    
    # Recalculate scores and dynamically choose the path[cite: 4]
    update_scores()
    target_port = select_best_path()
    
    if not target_port:
        print("CRITICAL: All paths are down! Network failure.")
        break
        
    while True:
        # Print the live scores so you can watch the algorithm making decisions
        print(f"Sent Seq {i} via port {target_port} | Scores -> R1: {paths[5001].get('score', 'X')} | R2: {paths[5002].get('score', 'X')}")
        sock.sendto(message_bytes, ('localhost', target_port))
        
        try:
            ack_data, _ = sock.recvfrom(1024)
            ack_json = json.loads(ack_data.decode('utf-8'))
            
            if ack_json.get("type") == "ACK" and ack_json.get("ack_sequence") == i:
                rtt_ms = (time.time() - current_time) * 1000
                # Use a moving average to smooth out sudden latency spikes (like OS concepts)
                old_latency = paths[target_port]["latency"]
                paths[target_port]["latency"] = round((old_latency * 0.7) + (rtt_ms * 0.3), 2)
                print(f"--> Success: ACK for seq {i} | Latency: {paths[target_port]['latency']}ms\n")
                break 
                
        except (socket.timeout, ConnectionResetError):
            print(f"*** FAILURE DETECTED: Router {target_port} is dead. Rerouting... ***")
            paths[target_port]["status"] = "failed"
            paths[target_port]["score"] = 9999 
            
            target_port = select_best_path()
            if not target_port:
                print("CRITICAL: All paths are down! Network failure.")
                break
                
    time.sleep(0.5)