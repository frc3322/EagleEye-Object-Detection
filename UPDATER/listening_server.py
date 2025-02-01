import socket
import threading
import struct
import os
import shutil
import zipfile
import tempfile

# Configuration
TCP_PORT = 332299  # Port for incoming TCP connections
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
        # First, read an 8-byte header that represents the file size
        header = recvall(conn, 8)
        if len(header) < 8:
            print(f"[TCP] Incomplete header received from {addr}")
            return

        file_size = struct.unpack('!Q', header)[0]
        print(f"[TCP] Expecting {file_size} bytes from {addr}")

        # Read the file data
        received = 0
        chunks = []
        while received < file_size:
            chunk = conn.recv(min(4096, file_size - received))
            if not chunk:
                break
            chunks.append(chunk)
            received += len(chunk)
        zip_data = b''.join(chunks)
        if len(zip_data) != file_size:
            print(f"[TCP] Error: Expected {file_size} bytes but received {len(zip_data)} bytes.")
            return

        # Save the received data as a temporary zip file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip_file:
            tmp_zip_file.write(zip_data)
            tmp_zip_name = tmp_zip_file.name
        print(f"[TCP] Received ZIP file saved as {tmp_zip_name}")

        # Create a temporary directory for extraction
        temp_extract_dir = tempfile.mkdtemp(prefix="extract_")

        try:
            with zipfile.ZipFile(tmp_zip_name, "r") as zip_ref:
                zip_ref.extractall(temp_extract_dir)
            print(f"[TCP] ZIP file extracted to {temp_extract_dir}")
        except Exception as e:
            print(f"[TCP] Error extracting ZIP file: {e}")
            return

        # Remove the current TARGET_FOLDER if it exists
        if os.path.exists(TARGET_FOLDER):
            shutil.rmtree(TARGET_FOLDER)
            print(f"[TCP] Removed existing folder: {TARGET_FOLDER}")

        # Now, determine how to re-create the TARGET_FOLDER.
        # If the ZIP file contained a single top-level folder, move it.
        # Otherwise, create TARGET_FOLDER and move all items in.
        extracted_items = os.listdir(temp_extract_dir)
        if len(extracted_items) == 1 and os.path.isdir(os.path.join(temp_extract_dir, extracted_items[0])):
            src_path = os.path.join(temp_extract_dir, extracted_items[0])
            shutil.move(src_path, TARGET_FOLDER)
            print(f"[TCP] Moved folder {src_path} to {TARGET_FOLDER}")
        else:
            os.makedirs(TARGET_FOLDER, exist_ok=True)
            for item in extracted_items:
                shutil.move(os.path.join(temp_extract_dir, item), TARGET_FOLDER)
            print(f"[TCP] Moved extracted items into {TARGET_FOLDER}")

    except Exception as e:
        print(f"[TCP] Error handling client {addr}: {e}")
    finally:
        conn.close()
        print(f"[TCP] Connection closed with {addr}")
        # Clean up temporary files/directories
        try:
            if os.path.exists(tmp_zip_name):
                os.remove(tmp_zip_name)
            if os.path.exists(temp_extract_dir):
                shutil.rmtree(temp_extract_dir)
        except Exception as cleanup_error:
            print(f"[TCP] Cleanup error: {cleanup_error}")

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
