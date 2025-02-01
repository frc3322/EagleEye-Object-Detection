import socket
import pickle

# Client setup
host = 'server_ip_address_here'  # Replace with the server's IP address
port = 12345                      # Port number that the server is listening on

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))

# Message to send
message = {'message': 'Hello from Windows client!'}
data = pickle.dumps(message)

# Send data to the server
client_socket.send(data)

# Close the connection
client_socket.close()
