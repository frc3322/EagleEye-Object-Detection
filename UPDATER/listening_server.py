#!/usr/bin/env python3
import os
import socket
import struct
import subprocess
import threading

BROADCAST_PORT = 5002
TRANSFER_PORT = 5001
TARGET_FOLDER = "/opt/scythevision"
SERVICE_NAME = "ScytheVision.service"

def broadcast_presence():
    """Broadcasts a presence message so clients can find the server."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    while True:
        sock.sendto(b"SERVER_HERE", ("<broadcast>", BROADCAST_PORT))
        threading.Event().wait(2)  # Broadcast every 2 seconds

def recvall(conn, n):
    """Receives exactly n bytes from the socket."""
    data = bytearray()
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def receive_folder(conn):
    """Receives and reconstructs the folder."""
    raw = recvall(conn, 4)
    if raw is None:
        return False
    num_files = struct.unpack("!I", raw)[0]

    print(f"[Server] Receiving {num_files} files...")

    for _ in range(num_files):
        raw = recvall(conn, 4)
        if raw is None:
            return False
        path_len = struct.unpack("!I", raw)[0]

        rel_path_bytes = recvall(conn, path_len)
        if rel_path_bytes is None:
            return False
        rel_path = rel_path_bytes.decode('utf-8')

        output_path = os.path.join(TARGET_FOLDER, rel_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        raw = recvall(conn, 8)
        if raw is None:
            return False
        file_size = struct.unpack("!Q", raw)[0]

        with open(output_path, 'wb') as f:
            received = 0
            while received < file_size:
                chunk_size = min(4096, file_size - received)
                chunk = recvall(conn, chunk_size)
                if chunk is None:
                    return False
                f.write(chunk)
                received += len(chunk)

        print(f"[Server] Received {rel_path} ({file_size} bytes)")

    return True

def restart_service():
    """Restarts the ScytheVision service."""
    print("[Server] Restarting service...")
    try:
        subprocess.run(["sudo", "systemctl", "restart", SERVICE_NAME], check=True)
        print("[Server] Service restarted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[Server] Failed to restart service: {e}")

def handle_client(conn, addr):
    """Handles a single client connection."""
    print(f"[Server] Connection from {addr}")
    with conn:
        if receive_folder(conn):
            print("[Server] Folder update complete.")
            restart_service()
        else:
            print("[Server] Folder update failed.")

def main():
    """Starts the server."""
    threading.Thread(target=broadcast_presence, daemon=True).start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.bind(("0.0.0.0", TRANSFER_PORT))
        server_sock.listen(5)
        print(f"[Server] Listening on port {TRANSFER_PORT}...")

        while True:
            conn, addr = server_sock.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
