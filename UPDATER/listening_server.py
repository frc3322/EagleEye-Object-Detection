import socket
import threading
import pickle
import os
import shutil

# Configuration
TCP_PORT = 12345       # Port for TCP connections (data exchange)
UDP_PORT = 54321       # Port for UDP discovery messages
DISCOVERY_MSG = "DISCOVER_SERVER"
RESPONSE_MSG = "SERVER_HERE"
RECEIVE_DIR = os.path.expanduser("../src")  # Directory to save received files

def udp_discovery_listener():
    """
    Listen for UDP discovery messages and reply with a response.
    """
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Allow reuse of addresses
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    udp_sock.bind(('', UDP_PORT))
    print(f"[UDP] Discovery listener started on port {UDP_PORT}")

    while True:
        try:
            data, addr = udp_sock.recvfrom(9988)
            message = data.decode('utf-8')
            if message == DISCOVERY_MSG:
                print(f"[UDP] Discovery request received from {addr}")
                udp_sock.sendto(RESPONSE_MSG.encode('utf-8'), addr)
        except Exception as e:
            print(f"[UDP] Error: {e}")

def remove_and_create_folder(target_dir):
    """
    Remove the existing folder (if any) and create a fresh folder.
    """
    if os.path.exists(target_dir):
        print(f"[TCP] Removing existing folder: {target_dir}")
        shutil.rmtree(target_dir)  # Remove the folder and its contents
    os.makedirs(target_dir)  # Create the folder again
    print(f"[TCP] Created folder: {target_dir}")

def save_file(file_info):
    """
    Save received file data to the server's filesystem.
    """
    file_name = file_info["file_name"]
    file_data = file_info["file_data"]
    file_path = os.path.join(RECEIVE_DIR, file_name)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'wb') as f:
        f.write(file_data)
    print(f"[TCP] Received and saved file: {file_path}")

def tcp_server():
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_sock.bind(('', TCP_PORT))
    tcp_sock.listen(1)
    print(f"[TCP] Server listening on port {TCP_PORT}")

    while True:
        conn, addr = tcp_sock.accept()
        print(f"[TCP] Connection accepted from {addr}")

        try:
            remove_and_create_folder(RECEIVE_DIR)

            while True:
                length_data = conn.recv(4)  # Read 4-byte length
                if not length_data:
                    break  # Connection closed
                length = int.from_bytes(length_data, 'big')

                data = b""
                while len(data) < length:
                    packet = conn.recv(length - len(data))
                    if not packet:
                        break
                    data += packet

                if data == b"EOF":  # End of transmission
                    print("[TCP] Folder transfer complete.")
                    break

                file_info = pickle.loads(data)  # Load data
                save_file(file_info)

        except Exception as e:
            print(f"[TCP] Error processing data: {e}")
        finally:
            conn.close()
            print(f"[TCP] Connection closed with {addr}")

if __name__ == '__main__':
    # Start UDP discovery listener in a background thread
    udp_thread = threading.Thread(target=udp_discovery_listener, daemon=True)
    udp_thread.start()

    # Start TCP server (runs in the main thread)
    tcp_server()
