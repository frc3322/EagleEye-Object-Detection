from ultralytics import YOLO

print("Loading model...")
model = YOLO('color_model.pt')
print("Model loaded.")

print("Exporting model to ONNX...")
model.export(format='onnx', dynamic=True, int8=True)
print("Model exported.")
