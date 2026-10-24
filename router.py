import socket
import sys
import time

listen_port = int(sys.argv[1])
forward_port = int(sys.argv[2])
router_name = sys.argv[3]

# Optional 4th argument: Artificial delay in seconds to simulate congestion
delay = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('localhost', listen_port))

print(f"{router_name} active. Listening on {listen_port} -> Forwarding to {forward_port}")
if delay > 0:
    print(f"[{router_name}] ⚠️ CONGESTION SIMULATION ON: Delaying packets by {delay} seconds")

while True:
    data, address = sock.recvfrom(1024)
    
    # Simulate network congestion before forwarding
    if delay > 0:
        time.sleep(delay)
        
    sock.sendto(data, ('localhost', forward_port))
    print(f"[{router_name}] Routed packet from {address} to {forward_port}")