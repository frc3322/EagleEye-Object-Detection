#!/usr/bin/env python3
import socket
import threading
import struct
import os
import shutil
import tempfile

# Configuration
UDP_PORT = 12346  # Port for receiving UDP broadcast for auto discovery
TCP_PORT = 12345  # Port for incoming TCP connections
TARGET_FOLDER = "FIRST-Object-Detection"  # Folder to replace

def recvall(sock, count):
    """Receive exactly 'count' bytes from the socket."""
    buf = b''
    while len(buf) < count:
        packet = sock.recv(count - len(buf))
        if not packet:
            break
        buf += packet
    return buf

def handle_client(conn, addr):
    print(f"[TCP] Connection accepted from {addr}")
    try:
        # First, receive the folder name (assuming it’s a UTF-8 encoded string)
        folder_name_len = struct.unpack('!I', recvall(conn, 4))[0]
        folder_name = recvall(conn, folder_name_len).decode('utf-8')

        # Receive folder contents
        while True:
            # Receive a file size header
            header = recvall(conn, 8)
            if len(header) < 8:
                break  # No more files to receive

            file_size = struct.unpack('!Q', header)[0]
            file_name_len = struct.unpack('!I', recvall(conn, 4))[0]
            file_name = recvall(conn, file_name_len).decode('utf-8')

            print(f"[TCP] Receiving file {file_name} ({file_size} bytes)")

            # Make sure the directory exists, then write the file
            target_dir = os.path.join(TARGET_FOLDER, folder_name)
            os.makedirs(target_dir, exist_ok=True)

            file_path = os.path.join(target_dir, file_name)
            with open(file_path, 'wb') as f:
                f.write(file_data)
            print(f"[TCP] File saved: {file_path}")

        print(f"[TCP] Finished receiving folder {folder_name} from {addr}")

    except Exception as e:
        print(f"[TCP] Error handling client {addr}: {e}")
    finally:
        conn.close()
        print(f"[TCP] Connection closed with {addr}")

def udp_broadcast_listener():
    # UDP socket for receiving the broadcast
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', UDP_PORT))
    print(f"[UDP] Listening for broadcast messages on port {UDP_PORT}...")

    while True:
        message, addr = sock.recvfrom(1024)  # Listen for broadcast messages
        if message == b"FIND_SERVER":
            print(f"[UDP] Broadcast received from {addr}. Sending server info back.")
            sock.sendto(f"{socket.gethostbyname(socket.gethostname())}:{TCP_PORT}".encode(), addr)

def tcp_server():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(('', TCP_PORT))
    server_sock.listen(5)
    print(f"[TCP] Server listening on port {TCP_PORT} ...")
    try:
        while True:
            conn, addr = server_sock.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            client_thread.start()
    except KeyboardInterrupt:
        print("\n[TCP] Server shutting down.")
    finally:
        server_sock.close()

if __name__ == '__main__':
    # Start UDP listener for auto-discovery
    udp_thread = threading.Thread(target=udp_broadcast_listener, daemon=True)
    udp_thread.start()

    # Start the TCP server
    tcp_server()
