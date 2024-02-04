import cv2
from time import time
from ultralytics import YOLO
from PIL import Image
import numpy as np

# Load video
cap = cv2.VideoCapture("IMG_1273.MOV")

# Get video properties
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

model = YOLO("runs/detect/note-detection-n2/weights/best.pt")
