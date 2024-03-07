import cv2
from time import time
from ultralytics import YOLO
from constants import ObjectDetectionConstants, DisplayConstants

image_size = (ObjectDetectionConstants.input_size, ObjectDetectionConstants.input_size)

# Load model
model = YOLO(ObjectDetectionConstants.model_path, task="detect")


def detect(image, verbose=False, return_image=False):
    """
    Detects notes in the given image
    :param image: the image to detect notes in
    :param verbose: print out the time taken and estimated FPS
    :param return_image: whether to return the image with the detected notes overlaid
    :return: returns the detections if return_image is False, otherwise returns the detections and the image with the
    detected notes overlaid (detections, image)
    """
    start = time()

    # Resize frame directly using the interpolation method for better quality
    image = cv2.resize(image, image_size)

    # Detect notes
    detections = model.predict(
        image,
        show=False,
        device="cpu",
        conf=ObjectDetectionConstants.confidence_threshold,
    )

    if return_image:
        for detection in detections:
            boxes = detection.boxes
            for box in boxes:
                conf = round(box.conf[0].item(), 2)

                x1, y1, x2, y2 = (
                    int(box.xyxy[0][0].item()),
                    int(box.xyxy[0][1].item()),
                    int(box.xyxy[0][2].item()),
                    int(box.xyxy[0][3].item()),
                )

                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    image,
                    str(conf),
                    (x1, y1),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )
        if verbose:
            print(f"Detection Time taken in ms: {(time() - start) * 1000}ms")
            print(f"Detection Estimated FPS: {1 / (time() - start)}")

        return detections, image

    if verbose:
        print(f"Detection Time taken in ms: {(time() - start) * 1000}ms")
        print(f"Detection Estimated FPS: {1 / (time() - start)}")

    return detections
