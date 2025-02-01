#!/usr/bin/env python3
import os
import socket
import struct
import shutil
import tkinter.filedialog as filedialog
import customtkinter as ctk
import threading

# ---------------------------
# Core functions (from client.py)
# ---------------------------
def zip_folder(folder_path):
    """
    Compress the specified folder into a zip archive.
    The zip archive is created in the current working directory.
    Returns the filename of the zip archive.
    """
    base_name = os.path.basename(os.path.normpath(folder_path))
    zip_file = shutil.make_archive(base_name, 'zip', folder_path)
    return zip_file

def send_file(server_ip, server_port, file_path, status_callback=None):
    """
    Sends a file to the specified server IP and port.
    status_callback (if provided) is a function that will be called with status messages.
    """
    file_size = os.path.getsize(file_path)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if status_callback:
                status_callback(f"Connecting to {server_ip}:{server_port} ...")
            sock.connect((server_ip, server_port))
            if status_callback:
                status_callback("Connected. Sending file size...")
            # Send file size (8 bytes, network byte order)
            sock.sendall(struct.pack("!Q", file_size))

            # Send the file data in chunks.
            sent = 0
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    sock.sendall(chunk)
                    sent += len(chunk)
                    if status_callback:
                        status_callback(f"Sent {sent} of {file_size} bytes...")
            if status_callback:
                status_callback("File transfer complete.")
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
        self.geometry("500x300")

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
        self.port_entry = ctk.CTkEntry(self, placeholder_text="Server Port (e.g., 5001)")
        self.port_entry.pack(pady=(0, 20))

        # Transfer button
        self.transfer_button = ctk.CTkButton(self, text="Transfer Folder", command=self.transfer_folder)
        self.transfer_button.pack(pady=(0, 20))

        # Status display (multi-line text box)
        self.status_text = ctk.CTkTextbox(self, width=480, height=100)
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
        # Retrieve server IP and port.
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

        # Run the file transfer in a separate thread to avoid blocking the GUI.
        threading.Thread(target=self.process_transfer, args=(server_ip, server_port), daemon=True).start()

    def process_transfer(self, server_ip, server_port):
        self.log_status("Compressing folder...")
        try:
            zip_file = zip_folder(self.folder_path)
            self.log_status(f"Created archive: {zip_file}")
        except Exception as e:
            self.log_status(f"Error compressing folder: {e}")
            return

        self.log_status("Starting file transfer...")
        # Define a callback to log status messages from send_file.
        def callback(msg):
            self.log_status(msg)
        send_file(server_ip, server_port, zip_file, status_callback=callback)

        # Clean up the temporary zip file.
        try:
            os.remove(zip_file)
            self.log_status("Temporary archive removed.")
        except Exception as e:
            self.log_status(f"Error removing temporary archive: {e}")

if __name__ == "__main__":
    app = ClientApp()
    app.mainloop()
