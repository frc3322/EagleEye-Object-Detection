from ultralytics import YOLO

# Load a model
print("Loading model...")
model = YOLO('color_model.pt')  # load an official model
print("Model loaded.")

# Export the model
print("Exporting model...")
model.export(format='onnx', imgsz=640)
print("Model exported.")
