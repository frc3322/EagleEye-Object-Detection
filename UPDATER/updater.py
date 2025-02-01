import os
import socket
import struct
import json

MULTICAST_GROUP = "239.255.255.250"
DISCOVERY_PORT = 5002
TRANSFER_PORT = 5001
CACHE_FILE = os.path.expanduser("~\\.folder_cache")

def discover_server():
    """Uses multicast to find the server."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(10)
        try:
            print("[Client] Searching for server...")
            sock.sendto(b"DISCOVER", (MULTICAST_GROUP, DISCOVERY_PORT))
            data, addr = sock.recvfrom(1024)
            if data == b"SERVER_HERE":
                print(f"[Client] Server found at {addr[0]}")
                return addr[0]
        except socket.timeout:
            print("[Client] No response from server.")
    return None

def load_cached_path():
    """Loads the cached folder path if available."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f).get("folder_path")
    return None

def save_cached_path(folder_path):
    """Saves the folder path to cache."""
    with open(CACHE_FILE, "w") as f:
        json.dump({"folder_path": folder_path}, f)

def send_folder(server_ip, folder_path):
    """Sends a folder to the server."""
    file_list = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, folder_path)
            file_list.append((rel_path, full_path))

    num_files = len(file_list)
    print(f"[Client] Sending {num_files} files to {server_ip}...")

    try:
        with socket.create_connection((server_ip, TRANSFER_PORT)) as sock:
            sock.sendall(struct.pack("!I", num_files))

            for rel_path, full_path in file_list:
                rel_path_bytes = rel_path.replace("\\", "/").encode('utf-8')  # Ensure cross-platform path compatibility
                sock.sendall(struct.pack("!I", len(rel_path_bytes)))
                sock.sendall(rel_path_bytes)

                file_size = os.path.getsize(full_path)
                sock.sendall(struct.pack("!Q", file_size))

                with open(full_path, 'rb') as f:
                    while chunk := f.read(4096):
                        sock.sendall(chunk)

                print(f"[Client] Sent {rel_path}")
        print("[Client] Folder transfer complete.")
    except Exception as e:
        print(f"[Client] Error: {e}")

if __name__ == "__main__":
    cached_path = load_cached_path()
    folder_path = input(f"Enter folder path (Press Enter to use cached: {cached_path}): ").strip() or cached_path

    if not folder_path or not os.path.isdir(folder_path):
        print("[Client] Invalid folder path.")
        exit(1)

    save_cached_path(folder_path)
    server_ip = discover_server()

    if server_ip:
        send_folder(server_ip, folder_path)
    else:
        print("[Client] No server found.")
