import cv2


# code that reads from camera 0 and displays the video feed
cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
