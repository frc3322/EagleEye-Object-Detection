from ultralytics import YOLO

# Load YOLO model
model = YOLO(r'/src/models/_GamePiece.pt')  # Replace with your model path

model_path = model.export(format='edgetpu')

print(model_path)
