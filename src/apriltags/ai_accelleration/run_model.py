import time
import cv2

from utils import (
    VIDEO_PATH,
    MODEL_PATH,
    CONF_THRESHOLD,
    AI_EVAL_FRAME_INTERVAL,
)
from apriltag_cnn_preprocessor import ApriltagCnnPreprocessor

SHOW_PREDICTIONS = True


def predict_video(
    video_path: str = VIDEO_PATH,
    model_path: str = MODEL_PATH,
    threshold: float = CONF_THRESHOLD,
) -> None:
    """Run predictions on a video using the AprilTag CNN preprocessor.

    Args:
        video_path: Path to the input video file.
        model_path: Path to the trained model weights.
        threshold: Confidence threshold for predictions.
    """
    try:
        preprocessor = ApriltagCnnPreprocessor(model_path, threshold)
    except Exception as e:
        print(f"Error initializing preprocessor: {e}")
        return

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Failed to open video: {video_path}")
        return

    frame_count = 0
    total_inference_time = 0.0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % AI_EVAL_FRAME_INTERVAL == 0:
            start_time = time.time()
            _, vis_frame = preprocessor.process_frame(frame, return_visualization=SHOW_PREDICTIONS)
            inference_time = time.time() - start_time

            if frame_count > 0:
                total_inference_time += inference_time
        else:
            if SHOW_PREDICTIONS:
                vis_frame = preprocessor.direct_visualize_frame(frame)

        if SHOW_PREDICTIONS:
            cv2.imshow("Prediction", vis_frame)
            key = cv2.waitKey(33)
            if key == 27:
                break

        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()

    if frame_count > 1:
        num_inference_frames = (frame_count - 1) // AI_EVAL_FRAME_INTERVAL
        if num_inference_frames > 0:
            avg_ms = (total_inference_time / num_inference_frames) * 1000
            print(
                f"Average inference time: {avg_ms:.2f} ms over {num_inference_frames} frames"
            )
    elif frame_count == 1:
        print(
            "Processed 1 frame. Average inference time calculation requires more than one frame."
        )
    else:
        print("No frames processed.")


if __name__ == "__main__":
    predict_video()
