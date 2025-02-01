from ultralytics import YOLO

# Load YOLO model
model = YOLO(r'/Users/darkeden/PycharmProjects/FIRST-Object-Detection/src/models/GamePiece.pt')  # Replace with your model path

model_path = model.export(format='edgetpu')

print(model_path)
