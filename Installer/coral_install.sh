#!/bin/bash
set -e  # Exit immediately if any command fails

ARCH=$(uname -m)

# Map system architecture to the correct package type
case "$ARCH" in
    "x86_64")
        PLATFORM="amd64"
        ;;
    "aarch64")
        PLATFORM="arm64"
        ;;
    "armv7l")
        PLATFORM="armhf"
        ;;
    *)
        echo "Unsupported architecture: $ARCH"
        exit 1
        ;;
esac

# Function to get the latest libedgetpu1-std release link
echo "Fetching latest libedgetpu1-std release link for $PLATFORM..."
LATEST_URL=$(curl -s https://api.github.com/repos/feranick/libedgetpu/releases/latest \
  | grep -oP '"browser_download_url": "\K(https://github.com/feranick/libedgetpu/releases/download/[^" ]+bookworm_'$PLATFORM'.deb)')

if [[ -z "$LATEST_URL" ]]; then
    echo "Error: Could not find the latest libedgetpu1-std package for $PLATFORM. Check the repository manually."
    exit 1
fi

echo "Downloading $LATEST_URL..."
wget "$LATEST_URL" -O libedgetpu1-std.bookworm_"$PLATFORM".deb

# Install the package
echo "Installing libedgetpu1-std..."
dpkg -i libedgetpu1-std.bookworm_"$PLATFORM".deb

# Activate virtual environment
if [[ -f "/root/EagleEye-Object-Detection/venv/bin/activate" ]]; then
    echo "Activating virtual environment..."
    . /root/EagleEye-Object-Detection/venv/bin/activate
else
    echo "Error: Virtual environment not found."
    exit 1
fi

# Uninstall existing TensorFlow packages
echo "Uninstalling TensorFlow..."
pip uninstall -y tensorflow tensorflow-aarch64 || true

# Install tflite-runtime
echo "Installing tflite-runtime..."
pip install -U tflite-runtime

echo "Setup complete! Your Coral TPU is ready."
