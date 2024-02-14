from ultralytics import YOLO

# Load a model
print("Loading model...")
model = YOLO(input("Enter the path of the model that you want to export (ending in .pt): "))
print("Model loaded.")

# Export the model
print("Exporting model...")
model.export(format='onnx', imgsz=640, simplify=True, device='cpu') # settings for exporting to co processer
print("Model exported.")
