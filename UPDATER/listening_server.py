#!/usr/bin/env python3
import socket
import threading
import struct
import os
import shutil
import tempfile

# Configuration
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

            # Receive the file content
            file_data = recvall(conn, file_size)

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
    tcp_server()
