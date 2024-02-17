import cv2
from time import time, sleep

start = time()
sleep(1)
print(f"Time taken in ms: {(time() - start) * 1000}ms")

# code that reads from camera 0 and displays the video feed
cap = cv2.VideoCapture(2)

while True:
    ret, frame = cap.read()
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
