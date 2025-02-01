import socket
import pickle

# Server setup
host = '0.0.0.0'  # Listen on all available interfaces
port = 12345       # Port to bind to
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)

print(f"Server listening on {host}:{port}")

# Accept connection from client
conn, addr = server_socket.accept()
print(f"Connected to {addr}")

# Receive and print data from the client
data = conn.recv(1024)
if data:
    message = pickle.loads(data)
    print("Received from client:", message)

# Close the connection
conn.close()
