#!/bin/bash
set -e  # Exit immediately if any command fails

SNAPSHOT_NAME="pre_install_$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="/root/system_backup"

echo "Installing timeshift"
apt install timeshift

echo "Saving machine state before installation..."

if command -v timeshift &> /dev/null; then
    timeshift --create --comments "Pre-install snapshot" --tags D --snapshot-device /  # Modify if needed
else
    echo "Timeshift not found, falling back to tar backup..."
    mkdir -p "$BACKUP_DIR"
    tar -czf "$BACKUP_DIR/backup.tar.gz" /etc /var /home
fi

trap 'echo "Installation failed! Restoring system..."; 
      if command -v timeshift &> /dev/null; then 
          timeshift --restore --snapshot $SNAPSHOT_NAME --yes;
      else 
          echo "Restoring from tar backup..."; 
          tar -xzf "$BACKUP_DIR/backup.tar.gz" -C /;
      fi
      exit 1' ERR

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
python -m venv venv
source venv/bin/activate

echo "Installing PyTorch..."
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo "Installing project dependencies..."
pip install -r requirements.txt

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
