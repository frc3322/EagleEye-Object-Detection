from ultralytics import YOLO
from detect_devices import detect_hardware
import os


def convert_model(model_path: str, regenerate: bool = False):
    gpu_present, tpu_present = detect_hardware()
    model_name_no_ext = os.path.basename(model_path).split(".")[0]

    if regenerate:
        print("Regenerating cached models")
        for file in os.listdir("cached_models"):
            os.remove(f"cached_models/{file}")

    if gpu_present:
        if os.path.exists(f"cached_models/{model_name_no_ext}.engine"):
            print("Using cached gpu model")
            return f"cached_models/{model_name_no_ext}.engine"
        print("Converting model to TensorRT")

        model = YOLO(model_path)
        model_path = model.export(format="TensorRT", device="gpu")
    elif tpu_present:
        if os.path.exists(f"cached_models/{model_name_no_ext}_edgetpu.tflite"):
            print("Using cached tpu model")
            return f"cached_models/{model_name_no_ext}_edgetpu.tflite"
        print("Converting model to EdgeTPU")

        model = YOLO(model_path)
        model_path = model.export(format="edgetpu")
    else:
        if os.path.exists(f"cached_models/{model_name_no_ext}.onnx"):
            print("Using cached onnx model")
            return f"cached_models/{model_name_no_ext}.onnx"
        print("Converting model to ONNX")

        model = YOLO(model_path)
        model_path = model.export(format="onnx")

    # move file to cached_models
    os.rename(model_path, f"cached_models/{os.path.basename(model_path)}")
    return f"cached_models/{os.path.basename(model_path)}", gpu_present, tpu_present
