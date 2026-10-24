import socket
import json
import time
import hashlib
import random
import threading
from flask import Flask, jsonify
from flask_cors import CORS

# --- FLASK API SETUP ---
app = Flask(__name__)
CORS(app) # Allows the React frontend to fetch data

# Global variables to expose to the dashboard
current_target = None
total_packets_sent = 0

@app.route('/api/metrics')
def get_metrics():
    return jsonify({
        "paths": paths,
        "current_target": current_target,
        "total_packets_sent": total_packets_sent
    })

def run_flask():
    # Run the API on port 8080 so it doesn't conflict with your network ports
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)

# Start the Flask API on a background thread
api_thread = threading.Thread(target=run_flask, daemon=True)
api_thread.start()
# -----------------------

# --- NETWORK SETUP ---
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('localhost', 4000))
sock.settimeout(2.0)

paths = {
    5001: {"status": "healthy", "latency": 1.0, "score": 0},
    5002: {"status": "healthy", "latency": 1.0, "score": 0}
}

W1_LATENCY = 1.0
W2_LOSS = 10.0
W3_CONGESTION = 1.0
W4_HOP = 1.0

def update_scores():
    for port, data in paths.items():
        if data["status"] == "healthy":
            data["score"] = round((W1_LATENCY * data["latency"]) + (W4_HOP * 1), 2)

def select_best_path():
    healthy_ports = [p for p, d in paths.items() if d["status"] == "healthy"]
    if not healthy_ports: return None
    if len(healthy_ports) == 1: return healthy_ports[0]
        
    score1 = paths[healthy_ports[0]]["score"]
    score2 = paths[healthy_ports[1]]["score"]
    total_score = score1 + score2
    
    prob_path_1 = score2 / total_score if total_score > 0 else 0.5
    return healthy_ports[0] if random.random() < prob_path_1 else healthy_ports[1]

# --- MAIN SENDER LOOP ---
for i in range(1, 10000):
    total_packets_sent = i
    payload_text = f"This is packet {i}"
    current_time = time.time()
    packet_hash = hashlib.sha256(f"{payload_text}{current_time}".encode('utf-8')).hexdigest()

    packet = {
        "sequence_number": i,
        "source_address": "localhost:4000",
        "destination_address": "localhost:5000",
        "payload": payload_text,
        "timestamp": current_time,
        "checksum": packet_hash
    }
    
    message_bytes = json.dumps(packet).encode('utf-8')
    update_scores()
    current_target = select_best_path()
    
    if not current_target:
        print("CRITICAL: All paths are down! Network failure.")
        break
        
    while True:
        print(f"Sent Seq {i} via {current_target} | Scores -> R1: {paths[5001].get('score', 'X')} | R2: {paths[5002].get('score', 'X')}")
        sock.sendto(message_bytes, ('localhost', current_target))
        
        try:
            ack_data, _ = sock.recvfrom(1024)
            ack_json = json.loads(ack_data.decode('utf-8'))
            
            if ack_json.get("type") == "ACK" and ack_json.get("ack_sequence") == i:
                rtt_ms = (time.time() - current_time) * 1000
                old_latency = paths[current_target]["latency"]
                paths[current_target]["latency"] = round((old_latency * 0.7) + (rtt_ms * 0.3), 2)
                break 
                
        except (socket.timeout, ConnectionResetError):
            print(f"*** FAILURE DETECTED: Router {current_target} is dead. Rerouting... ***")
            paths[current_target]["status"] = "failed"
            paths[current_target]["score"] = 9999 
            
            current_target = select_best_path()
            if not current_target:
                break
                
    time.sleep(0.5)