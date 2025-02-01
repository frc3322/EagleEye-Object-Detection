#!/usr/bin/env python3
import os
import socket
import struct
import subprocess
import zipfile

def receive_file(conn, output_file):
    """
    Receives a file from the connected socket and writes it to output_file.
    Returns True on success.
    """
    # First, receive the file size (8 bytes).
    raw_size = recvall(conn, 8)
    if raw_size is None:
        print("[Server] Failed to receive file size.")
        return False
    file_size = struct.unpack("!Q", raw_size)[0]
    print(f"[Server] Expecting file of size: {file_size} bytes.")

    received = 0
    with open(output_file, 'wb') as f:
        while received < file_size:
            # Receive in chunks.
            chunk = conn.recv(4096)
            if not chunk:
                break
            f.write(chunk)
            received += len(chunk)
            print(f"[Server] Received {received}/{file_size} bytes", end='\r')
    print("\n[Server] File reception complete.")
    return True

def recvall(conn, n):
    """Helper function to receive n bytes or return None if EOF is hit."""
    data = bytearray()
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def update_folder(zip_file, target_folder):
    """
    Extracts the zip_file into target_folder.
    Overwrites existing files.
    """
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(target_folder)
    print(f"[Server] Updated folder '{target_folder}' from {zip_file}.")

def restart_service(service_name):
    """
    Restarts the specified service using systemctl.
    """
    print(f"[Server] Restarting service: {service_name}")
    try:
        subprocess.run(["sudo", "systemctl", "restart", service_name], check=True)
        print(f"[Server] Service '{service_name}' restarted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[Server] Failed to restart service: {e}")

def main():
    listen_ip = "0.0.0.0"
    listen_port = 5001
    temp_zip = "/tmp/update.zip"  # Temporary file for the received archive.
    target_folder = "/opt/scythevision"  # Folder to update.
    service_name = "ScytheVision.service"

    # Create a TCP socket.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.bind((listen_ip, listen_port))
        server_sock.listen(5)
        print(f"[Server] Listening on {listen_ip}:{listen_port} ...")

        while True:
            try:
                conn, addr = server_sock.accept()
                print(f"[Server] Connection established from {addr}")
                with conn:
                    # Receive the file.
                    if receive_file(conn, temp_zip):
                        # Update folder from the received zip.
                        update_folder(temp_zip, target_folder)
                        # Remove the temporary zip file.
                        try:
                            os.remove(temp_zip)
                            print("[Server] Temporary archive removed.")
                        except Exception as e:
                            print(f"[Server] Error removing temporary archive: {e}")
                        # Restart the service.
                        restart_service(service_name)
                    else:
                        print("[Server] File reception failed.")
            except Exception as e:
                print(f"[Server] Error handling connection: {e}")

if __name__ == "__main__":
    main()
