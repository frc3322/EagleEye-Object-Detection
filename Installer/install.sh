#!/bin/bash
set -e  # Exit immediately if any command fails

echo "Updating and upgrading the system..."
apt update && apt upgrade -y

echo "Installing libgl1 (required for YOLO)..."
apt install -y libgl1

echo "Installing Python3 and pip..."
apt install python3-pip -y

echo "Cloning Repo..."
git clone "https://github.com/frc3322/EagleEye-Object-Detection.git"

echo "Navigating to EagleEye-Object-Detection directory..."
cd /root/EagleEye-Object-Detection/

echo "Creating and activating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing PyTorch..."
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo "Installing project dependencies..."
pip3 install -r requirements.txt

echo "Copying service files to systemd directory..."
cp /root/EagleEye-Object-Detection/Installer/EagleEye.service /etc/systemd/system/
cp /root/EagleEye-Object-Detection/Installer/EagleEyeUpdater.service /etc/systemd/system/

echo "Reloading systemd daemon..."
systemctl daemon-reload

echo "Enabling services..."
systemctl enable EagleEye.service
systemctl enable EagleEyeUpdater.service

echo "Starting services..."
systemctl start EagleEye.service
systemctl start EagleEyeUpdater.service

echo "Setup complete."
