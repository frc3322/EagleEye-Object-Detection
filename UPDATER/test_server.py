import socket
import threading
import pickle

# Configuration
TCP_PORT = 12345       # Port for TCP connections (data exchange)
UDP_PORT = 54321       # Port for UDP discovery messages
DISCOVERY_MSG = "DISCOVER_SERVER"
RESPONSE_MSG = "SERVER_HERE"

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
            data, addr = udp_sock.recvfrom(1024)
            message = data.decode('utf-8')
            if message == DISCOVERY_MSG:
                print(f"[UDP] Discovery request received from {addr}")
                udp_sock.sendto(RESPONSE_MSG.encode('utf-8'), addr)
        except Exception as e:
            print(f"[UDP] Error: {e}")

def tcp_server():
    """
    TCP server to accept client connections and receive data.
    """
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.bind(('', TCP_PORT))
    tcp_sock.listen(1)
    print(f"[TCP] Server listening on port {TCP_PORT}")

    while True:
        conn, addr = tcp_sock.accept()
        print(f"[TCP] Connection accepted from {addr}")
        try:
            data = conn.recv(1024)
            if data:
                # Unpickle the data received from the client
                message = pickle.loads(data)
                print(f"[TCP] Received message: {message}")
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
