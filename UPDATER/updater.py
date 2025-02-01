import socket
import pickle
import os
from time import sleep

# Configuration
TCP_PORT = 12345       # Must match the server's TCP port
UDP_PORT = 54321       # Must match the server's UDP discovery port
DISCOVERY_MSG = "DISCOVER_SERVER"
RESPONSE_MSG = "SERVER_HERE"
BROADCAST_ADDR = '<broadcast>'  # Special address for UDP broadcast

def discover_server(timeout=3):
    """
    Send a UDP broadcast to discover the server.
    Returns the server's IP address if found, otherwise None.
    """
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_sock.settimeout(timeout)

    try:
        print("[UDP] Sending discovery broadcast...")
        udp_sock.sendto(DISCOVERY_MSG.encode('utf-8'), (BROADCAST_ADDR, UDP_PORT))
        data, addr = udp_sock.recvfrom(9988)
        if data.decode('utf-8') == RESPONSE_MSG:
            print(f"[UDP] Server discovered at {addr[0]}")
            return addr[0]
    except socket.timeout:
        print("[UDP] Discovery timed out. No server found.")
    except Exception as e:
        print(f"[UDP] Error during discovery: {e}")

    return None

def send_folder(folder_path, tcp_sock):
    """
    Send the folder contents to the server.
    """
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'rb') as f:
                file_data = f.read()
                file_info = {"file_name": os.path.relpath(file_path, folder_path), "file_data": file_data}
                tcp_sock.send(pickle.dumps(file_info))  # Send each file one by one
                print(f"[TCP] Sent file: {file_path}")
    tcp_sock.send(b"EOF")  # End of folder transmission
    print("[TCP] Folder transfer complete.")

def tcp_client(server_ip, folder_path):
    """
    Connect to the server via TCP and send a folder.
    """
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print(f"[TCP] Connecting to server at {server_ip}:{TCP_PORT} ...")
        tcp_sock.connect((server_ip, TCP_PORT))
        sleep(5)
        send_folder(folder_path, tcp_sock)
        print("[TCP] Folder sent successfully.")
    except Exception as e:
        print(f"[TCP] Error: {e}")
    finally:
        tcp_sock.close()

if __name__ == '__main__':
    folder_path = "src"  # Replace with actual folder path
    server_ip = discover_server()
    if server_ip:
        tcp_client(server_ip, folder_path)
    else:
        print("Server could not be discovered.")
