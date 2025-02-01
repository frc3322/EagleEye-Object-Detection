#!/usr/bin/env python3
import os
import socket
import struct
import threading
import tkinter.filedialog as filedialog
import customtkinter as ctk

# ---------------------------
# Core functions for sending a folder (without zipping)
# ---------------------------
def send_folder(server_ip, server_port, folder_path, status_callback=None):
    """
    Sends the contents of folder_path to the server.

    Protocol:
      1. Send a 4-byte unsigned integer: number of files.
      2. For each file (found via os.walk):
         a. Send a 4-byte unsigned integer: length of the file’s relative path in bytes.
         b. Send the relative file path (UTF-8 encoded).
         c. Send an 8-byte unsigned long long: file size in bytes.
         d. Send the file’s data.
    """
    # Build list of files to send.
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            full_path = os.path.join(root, file)
            # Compute path relative to folder_path.
            rel_path = os.path.relpath(full_path, folder_path)
            file_list.append((rel_path, full_path))
    num_files = len(file_list)
    if status_callback:
        status_callback(f"Found {num_files} files to send.")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if status_callback:
                status_callback(f"Connecting to {server_ip}:{server_port} ...")
            sock.connect((server_ip, server_port))
            if status_callback:
                status_callback("Connected to server.")
            # Send number of files (4 bytes).
            sock.sendall(struct.pack("!I", num_files))

            # Loop through files.
            for rel_path, full_path in file_list:
                # Send relative path length and relative path.
                rel_path_bytes = rel_path.encode('utf-8')
                path_len = len(rel_path_bytes)
                sock.sendall(struct.pack("!I", path_len))
                sock.sendall(rel_path_bytes)

                # Get file size and send it (8 bytes).
                file_size = os.path.getsize(full_path)
                sock.sendall(struct.pack("!Q", file_size))

                # Send the file data.
                sent = 0
                with open(full_path, 'rb') as f:
                    while sent < file_size:
                        chunk = f.read(4096)
                        if not chunk:
                            break
                        sock.sendall(chunk)
                        sent += len(chunk)
                        if status_callback:
                            status_callback(f"Sending {rel_path}... ({sent}/{file_size} bytes)")
                if status_callback:
                    status_callback(f"Finished sending {rel_path}.")

            if status_callback:
                status_callback("Folder transfer complete.")
    except Exception as e:
        if status_callback:
            status_callback(f"Error during transfer: {e}")

# ---------------------------
# CustomTkinter GUI Application
# ---------------------------
class ClientApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Folder Update Client")
        self.geometry("500x350")

        # Folder selection
        self.folder_path = ""
        self.folder_button = ctk.CTkButton(self, text="Select Folder", command=self.select_folder)
        self.folder_button.pack(pady=(20, 10))

        self.folder_label = ctk.CTkLabel(self, text="No folder selected")
        self.folder_label.pack()

        # Server IP entry
        self.ip_entry = ctk.CTkEntry(self, placeholder_text="Server IP (e.g., 192.168.1.100)")
        self.ip_entry.pack(pady=(20, 10))

        # Server Port entry
        self.port_entry = ctk.CTkEntry(self, placeholder_text="Server Port (e.g., 3329)")
        self.port_entry.pack(pady=(0, 20))

        # Transfer button
        self.transfer_button = ctk.CTkButton(self, text="Transfer Folder", command=self.transfer_folder)
        self.transfer_button.pack(pady=(0, 20))

        # Status display (multi-line text box)
        self.status_text = ctk.CTkTextbox(self, width=480, height=120)
        self.status_text.pack(pady=(0, 10))
        self.status_text.insert("end", "Status messages will appear here...\n")
        self.status_text.configure(state="disabled")

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path = folder
            self.folder_label.configure(text=f"Folder: {folder}")
            self.log_status("Folder selected.")

    def log_status(self, message):
        """Append a message to the status text box."""
        self.status_text.configure(state="normal")
        self.status_text.insert("end", message + "\n")
        self.status_text.see("end")
        self.status_text.configure(state="disabled")

    def transfer_folder(self):
        server_ip = self.ip_entry.get().strip()
        port_str = self.port_entry.get().strip()
        if not self.folder_path:
            self.log_status("Error: No folder selected.")
            return
        if not server_ip or not port_str:
            self.log_status("Error: Please provide both Server IP and Port.")
            return
        try:
            server_port = int(port_str)
        except ValueError:
            self.log_status("Error: Port must be an integer.")
            return

        # Run the transfer in a separate thread.
        threading.Thread(target=self.process_transfer, args=(server_ip, server_port), daemon=True).start()

    def process_transfer(self, server_ip, server_port):
        self.log_status("Starting folder transfer...")
        send_folder(server_ip, server_port, self.folder_path, status_callback=self.log_status)

if __name__ == "__main__":
    app = ClientApp()
    app.mainloop()
