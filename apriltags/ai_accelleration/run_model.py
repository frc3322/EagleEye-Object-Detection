import time

import cv2
import numpy as np
import torch
from PIL import Image
from torchvision import transforms

from predictor import GridPredictor
from utils import (
    SCALE_FACTOR,
    CONF_THRESHOLD,
    VIDEO_PATH,
    MODEL_PATH,
    scale_with_aspect,
    ScaleTransform,
    calculate_crop_regions_from_grid,
    AI_EVAL_FRAME_INTERVAL,
)


def predict_video(
    video_path: str = VIDEO_PATH,
    model_path: str = MODEL_PATH,
    threshold: float = CONF_THRESHOLD,
) -> None:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = GridPredictor().to(device)

    try:
        model.load_state_dict(torch.load(model_path, map_location=device))
    except FileNotFoundError:
        print(f"Model file not found at {model_path}")
        return
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    model.eval()

    tf = transforms.Compose(
        [
            ScaleTransform(SCALE_FACTOR),
            transforms.ToTensor(),
        ]
    )

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Failed to open video: {video_path}")
        return

    frame_count = 0
    total_inference_time = 0.0
    last_probs = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_disp = scale_with_aspect(frame, SCALE_FACTOR)

        # Only run AI evaluation every AI_EVAL_FRAME_INTERVAL frames
        if frame_count % AI_EVAL_FRAME_INTERVAL == 0:
            img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            img_scaled_pil = scale_with_aspect(img_pil, SCALE_FACTOR)
            tensor = tf(img_scaled_pil).unsqueeze(0).to(device)

            with torch.no_grad():
                if device.type == "cuda":
                    torch.cuda.synchronize()
                start_time = time.time()
                logits = model(tensor)
                if device.type == "cuda":
                    torch.cuda.synchronize()
                inference_time = time.time() - start_time

                if frame_count > 0:
                    total_inference_time += inference_time

                probs = torch.sigmoid(logits)[0].cpu().numpy()
                last_probs = probs  # Store the last valid probabilities
        else:
            # Use the last valid probabilities for visualization
            probs = last_probs if last_probs is not None else np.zeros((10, 10))

        vis_frame = overlay_grid_cv2(frame_disp, probs, conf_threshold=threshold)

        cv2.imshow("Prediction", vis_frame)
        key = cv2.waitKey(1)
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


def overlay_grid_cv2(
    frame: np.ndarray, grid: np.ndarray, conf_threshold: float = 0.5
) -> np.ndarray:
    h, w, _ = frame.shape
    cell_w = w // 10
    cell_h = h // 10

    overlay = frame.copy()
    conf_grid_mask = grid >= conf_threshold

    for row in range(10):
        for column in range(10):
            left = column * cell_w
            top = row * cell_h
            right = left + cell_w
            bottom = top + cell_h

            if not conf_grid_mask[row, column]:
                cv2.rectangle(overlay, (left, top), (right, bottom), (0, 0, 0), -1)

            cv2.rectangle(overlay, (left, top), (right, bottom), (255, 255, 255), 1)

    cv2.addWeighted(overlay, 1, frame, 0, 0, frame)

    crop_regions = calculate_crop_regions_from_grid(conf_grid_mask, cell_w, cell_h)
    for region in crop_regions:
        left, top, right, bottom = region
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

    return frame


if __name__ == "__main__":
    predict_video()
