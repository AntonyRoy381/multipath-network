import socket
import sys

# Read configuration from the command line arguments
listen_port = int(sys.argv[1])
forward_port = int(sys.argv[2])
router_name = sys.argv[3]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('localhost', listen_port))

print(f"{router_name} is active. Listening on port {listen_port} -> Forwarding to port {forward_port}")

while True:
    data, address = sock.recvfrom(1024)
    # Forward the raw bytes directly to the next hop (the receiver)
    sock.sendto(data, ('localhost', forward_port))
    print(f"[{router_name}] Routed packet from {address} to port {forward_port}")