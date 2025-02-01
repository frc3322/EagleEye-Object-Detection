#!/usr/bin/env python3
import os
import socket
import struct
import configparser
import time

# Configuration
TCP_PORT = 12345  # Must match the server's TCP port
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

def send_folder_to_server(folder_path, server_ip):
    """
    Open the folder, send its contents (files) to the server.
    """
    folder_name = os.path.basename(folder_path)
    print(f"[CLIENT] Sending folder: {folder_name}")

    # Create a TCP socket and connect to the server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((server_ip, TCP_PORT))
        print(f"[CLIENT] Connected to server {server_ip}:{TCP_PORT}")

        # Send folder name first
        folder_name_len = len(folder_name)
        sock.sendall(struct.pack('!I', folder_name_len))
        sock.sendall(folder_name.encode('utf-8'))

        # Iterate over the files in the folder and send them one by one
        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                file_size = os.path.getsize(file_path)

                # Send file size and name
                sock.sendall(struct.pack('!Q', file_size))
                sock.sendall(struct.pack('!I', len(file_name)))
                sock.sendall(file_name.encode('utf-8'))

                # Send the file content
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                    sock.sendall(file_data)

                print(f"[CLIENT] Sent file: {file_name}")

        print("[CLIENT] Folder sent successfully.")

    except Exception as e:
        print(f"[CLIENT] Error sending folder: {e}")
    finally:
        sock.close()
        print(f"[CLIENT] Connection closed.")

if __name__ == '__main__':
    # Get the folder path from the user or config
    folder_path = get_folder_path()
    print(f"[CLIENT] Using folder: {folder_path}")

    # Ask for the server IP address
    server_ip = input("Enter the server IP address: ").strip()

    # Send the folder to the server
    send_folder_to_server(folder_path, server_ip)

    print("[CLIENT] Done.")
