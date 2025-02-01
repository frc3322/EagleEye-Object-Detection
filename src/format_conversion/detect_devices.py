import torch
import subprocess
import platform

def check_nvidia_gpu():
    try:
        return torch.cuda.is_available()
    except Exception:
        return False

def check_amd_gpu():
    try:
        if platform.system() == "Windows":
            result = subprocess.run(["wmic", "path", "win32_VideoController", "get", "Name"], capture_output=True, text=True)
        else:
            result = subprocess.run(["lspci"], capture_output=True, text=True)
        return "AMD" in result.stdout
    except Exception:
        return False

def check_coral_tpu():
    try:
        result = subprocess.run(["lsusb"], capture_output=True, text=True)
        return "Global Unichip Corp" in result.stdout
    except Exception:
        return False

def detect_hardware():
    """
    Detects the hardware available
    :return: tuple of (gpu_available, tpu_available)
    """
    gpu_available = check_nvidia_gpu() or check_amd_gpu()
    tpu_available = check_coral_tpu()
    print(f"GPU Available: {gpu_available}")
    print(f"TPU Available: {tpu_available}")
    return gpu_available, tpu_available

if __name__ == "__main__":
    gpu, tpu = detect_hardware()
    print(f"GPU Available: {gpu}")
    print(f"TPU Available: {tpu}")
