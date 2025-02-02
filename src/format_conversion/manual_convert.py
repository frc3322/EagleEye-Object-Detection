from ultralytics import YOLO

# Load YOLO model
model = YOLO(r'E:\Ceph-Mirror\Python-Files\Projects\FIRST-Note-Detection\src\models\GamePiece.pt')  # Replace with your model path

model_path = model.export(format='edgetpu')

print(model_path)
