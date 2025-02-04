from ultralytics import YOLO
from format_conversion.detect_devices import detect_hardware
from src.custom_logging.log import log
import os

def convert_model(model_path: str, regenerate: bool = False):
    gpu_present, tpu_present = detect_hardware()
    model_name_no_ext = os.path.basename(model_path).split(".")[0]

    if regenerate:
        log("Regenerating cached models")
        for file in os.listdir("cached_models"):
            os.remove(f"cached_models/{file}")

    if gpu_present:
        # check if model already is .engine
        if ".engine" in model_path:
            log("Model already converted")
            return model_path

        if os.path.exists(f"cached_models/{model_name_no_ext}.engine"):
            log("Using cached gpu model")
            return f"cached_models/{model_name_no_ext}.engine"
        log("Converting model to TensorRT")

        model = YOLO(model_path)
        model_path = model.export(format="TensorRT", device="gpu")
        log(f"Successfully converted to TensorRT: {model_path}")
    elif tpu_present:
        if "_edgetpu.tflite" in model_path:
            log("Model already converted")
            return model_path

        if os.path.exists(f"cached_models/{model_name_no_ext}_edgetpu.tflite"):
            log("Using cached tpu model")
            return f"cached_models/{model_name_no_ext}_edgetpu.tflite"
        log("Converting model to EdgeTPU")

        model = YOLO(model_path)
        model_path = model.export(format="edgetpu")
        log(f"Model converted successfully to EdgeTPU: {model_path}")
    else:
        if ".onnx" in model_path:
            log("Model already converted")
            return model_path

        if os.path.exists(f"cached_models/{model_name_no_ext}.onnx"):
            log("Using cached onnx model")
            return f"cached_models/{model_name_no_ext}.onnx"
        log("Converting model to ONNX")

        model = YOLO(model_path)
        model_path = model.export(format="onnx")
        log(f"Model converted successfully to ONNX: {model_path}")

    log(f"Moving model to cached_models/{os.path.basename(model_path)}")
    os.rename(model_path, f"cached_models/{os.path.basename(model_path)}")
    log(f"Successfully moved model to cached_models/{os.path.basename(model_path)}")

    return f"cached_models/{os.path.basename(model_path)}", gpu_present, tpu_present
