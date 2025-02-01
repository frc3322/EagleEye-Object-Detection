import os
import socket
import struct
import tempfile
import shutil  # For make_archive
import configparser

# Configuration
TCP_PORT = 3399  # Must match the server's TCP port
CONFIG_FILE = "client_config.ini"  # To cache the folder path

def get_folder_path():
    """
    Check for a cached folder path in CONFIG_FILE.
    If found, ask the user if they want to use it.
    Otherwise, ask the user to provide a folder path.
    """
    config = configparser.ConfigParser()
    folder_path = None

    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        if "Settings" in config and "folder_path" in config["Settings"]:
            cached_path = config["Settings"]["folder_path"]
            use_cached = input(f"Use cached folder path '{cached_path}'? (Y/n): ").strip().lower()
            if use_cached in ("", "y", "yes"):
                folder_path = cached_path

    while not folder_path or not os.path.isdir(folder_path):
        folder_path = input("Enter the full path to the folder you want to send: ").strip()
        if not os.path.isdir(folder_path):
            print("The provided path is not a valid folder. Please try again.")

    # Cache the folder path in the config file.
    if "Settings" not in config:
        config["Settings"] = {}
    config["Settings"]["folder_path"] = folder_path
    with open(CONFIG_FILE, "w") as configfile:
        config.write(configfile)
    return folder_path

def create_zip_of_folder(folder_path):
    """
    Compress the given folder into a ZIP file.
    Returns the full path to the created ZIP file.
    """
    # Create a temporary file (we only need the base name; shutil.make_archive adds .zip)
    temp_dir = tempfile.mkdtemp(prefix="ziptemp_")
    base_name = os.path.join(temp_dir, "archive")
    # Create the zip archive. This will zip the folder contents.
    # The archive will contain the folder's base name as the top-level folder.
    archive_path = shutil.make_archive(base_name, 'zip', root_dir=folder_path)
    return archive_path, temp_dir

def send_zip_to_server(zip_path, server_ip):
    """
    Open the ZIP file, send its size and contents to the server.
    """
    filesize = os.path.getsize(zip_path)
    print(f"[TCP] Preparing to send {filesize} bytes to server {server_ip}:{TCP_PORT}")

    with open(zip_path, "rb") as f:
        file_data = f.read()

    # Create a TCP socket and connect
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((server_ip, TCP_PORT))
        # First send 8 bytes representing the file size in network byte order
        sock.sendall(struct.pack('!Q', filesize))
        # Then send the file data
        sock.sendall(file_data)
        print("[TCP] File sent successfully.")
    except Exception as e:
        print(f"[TCP] Error sending file: {e}")
    finally:
        sock.close()

if __name__ == '__main__':
    # Get the folder path from the user or config
    folder_path = get_folder_path()
    print(f"[CLIENT] Using folder: {folder_path}")

    # Create a zip archive of the folder
    zip_path, temp_dir = create_zip_of_folder(folder_path)
    print(f"[CLIENT] Created ZIP archive: {zip_path}")

    # Ask for the server IP address
    server_ip = input("Enter the server IP address: ").strip()

    # Send the zip archive to the server
    send_zip_to_server(zip_path, server_ip)

    # Clean up the temporary zip and directory
    try:
        if os.path.exists(zip_path):
            os.remove(zip_path)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except Exception as cleanup_error:
        print(f"[CLIENT] Cleanup error: {cleanup_error}")

    print("[CLIENT] Done.")
