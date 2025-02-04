# Function to get the latest libedgetpu1-std release link
echo "Fetching latest libedgetpu1-std release link..."
LATEST_URL=$(curl -s https://api.github.com/repos/feranick/libedgetpu/releases/latest \
  | grep -oP '"browser_download_url": "\K(https://github.com/feranick/libedgetpu/releases/download/[^" ]+bookworm_arm64.deb)')

if [[ -z "$LATEST_URL" ]]; then
    echo "Error: Could not find the latest libedgetpu1-std package. Check the repository manually."
    exit 1
fi

echo "Downloading $LATEST_URL..."
wget "$LATEST_URL" -O libedgetpu1-std.bookworm_arm64.deb

# Install the package
echo "Installing libedgetpu1-std..."
dpkg -i libedgetpu1-std.bookworm_arm64.deb

source /root/EagleEye-Object-Detection/venv/bin/activate

# Uninstall existing TensorFlow packages
echo "Uninstalling TensorFlow..."
pip uninstall -y tensorflow tensorflow-aarch64

# Install tflite-runtime
echo "Installing tflite-runtime..."
pip install -U tflite-runtime

echo "Setup complete! Your Coral TPU is ready."
