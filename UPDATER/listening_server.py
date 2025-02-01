#!/usr/bin/env python3
import os
import socket
import struct
import subprocess

def recvall(conn, n):
    """Helper function to receive exactly n bytes from the socket."""
    data = bytearray()
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def receive_folder(conn, target_folder):
    """
    Receives a folder structure from the client and writes files to target_folder.

    Protocol:
      1. Read 4 bytes: unsigned int number of files.
      2. For each file:
         a. Read 4 bytes: unsigned int length of relative file path.
         b. Read the relative file path.
         c. Read 8 bytes: unsigned long long file size.
         d. Read file data and write to target_folder/relative_path.
    """
    # Receive number of files.
    raw = recvall(conn, 4)
    if raw is None:
        print("[Server] Failed to receive file count.")
        return False
    num_files = struct.unpack("!I", raw)[0]
    print(f"[Server] Expecting {num_files} files.")

    for i in range(num_files):
        # Receive relative path length.
        raw = recvall(conn, 4)
        if raw is None:
            print("[Server] Failed to receive path length.")
            return False
        path_len = struct.unpack("!I", raw)[0]

        # Receive the relative path.
        rel_path_bytes = recvall(conn, path_len)
        if rel_path_bytes is None:
            print("[Server] Failed to receive file path.")
            return False
        rel_path = rel_path_bytes.decode('utf-8')

        # Determine full output path.
        output_path = os.path.join(target_folder, rel_path)
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Receive file size.
        raw = recvall(conn, 8)
        if raw is None:
            print("[Server] Failed to receive file size.")
            return False
        file_size = struct.unpack("!Q", raw)[0]

        # Receive file data.
        received = 0
        with open(output_path, 'wb') as f:
            while received < file_size:
                chunk_size = 4096 if file_size - received >= 4096 else file_size - received
                chunk = recvall(conn, chunk_size)
                if chunk is None:
                    print("[Server] Connection lost while receiving file data.")
                    return False
                f.write(chunk)
                received += len(chunk)
        print(f"[Server] Received file: {rel_path} ({file_size} bytes)")
    return True

def restart_service(service_name):
    """Restarts the given service using systemctl."""
    print(f"[Server] Restarting service: {service_name}")
    try:
        subprocess.run(["sudo", "systemctl", "restart", service_name], check=True)
        print(f"[Server] Service '{service_name}' restarted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[Server] Failed to restart service: {e}")

def main():
    listen_ip = "10.0.0.158"
    listen_port = 3329
    target_folder = "/FIRST-Note-Detection"  # Folder to update
    service_name = "ScytheVision.service"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.bind((listen_ip, listen_port))
        server_sock.listen(5)
        print(f"[Server] Listening on {listen_ip}:{listen_port} ...")

        while True:
            try:
                conn, addr = server_sock.accept()
                print(f"[Server] Connection from {addr}")
                with conn:
                    if receive_folder(conn, target_folder):
                        print("[Server] Folder update complete.")
                        # Restart the service.
                        restart_service(service_name)
                    else:
                        print("[Server] Folder update failed.")
            except Exception as e:
                print(f"[Server] Error: {e}")

if __name__ == "__main__":
    main()
