import cv2
import numpy as np
from roboflow import Roboflow
from inference_sdk import InferenceHTTPClient 
from dotenv import load_dotenv
import os
import json

load_dotenv()
api_key = os.getenv("API_KEY")

# Load model once at import time (instead of inside main script body)
rf = Roboflow(api_key=api_key)
project = rf.workspace("giangproject").project("clothing-detection-p8vmn")
model = project.version(6).model

DATA_PATH = "data.json"


def run_model_on_image(image_path, image_name: str, confidence=80, overlap=30, show_windows=False):
    """
    Run clothing-detection model on a single image path.

    Returns:
        predictions: raw results.json()['predictions'] from Roboflow
        new_items: list of dicts that were appended to data.json
    """
    # --- 1. Run inference on the given image path ---
    results = model.predict(image_path, confidence=confidence, overlap=overlap)
    results_json = results.json()
    predictions = results_json.get("predictions", [])

    print("Predictions:", results_json)
    print(f"Items detected: {len(predictions)}")

    # --- 2. Load the image for cropping ---
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image at {image_path}")

    if show_windows:
        cv2.imshow("Original", img)

    # --- 4. Process detections and save crops ---
    if predictions:
        for i, item in enumerate(predictions):
            # Calculate coordinates
            x = int(item["x"] - item["width"] / 2)
            y = int(item["y"] - item["height"] / 2)
            w = int(item["width"])
            h = int(item["height"])

            # Skip if too small (less than 50x50 pixels)
            if w < 50 or h < 50:
                print(f"Skipping detection {i+1}: too small ({w}x{h})")
                continue

            # Boundary checking
            x = max(0, x)
            y = max(0, y)
            x2 = min(img.shape[1], x + w)
            y2 = min(img.shape[0], y + h)

            # Just crop - no drawing
            crop = img[y:y2, x:x2]

            # Save crop
            filename = f"images/{image_name}_crop_{i}.jpg"
            cv2.imwrite(filename, crop)
            print(f"Saved: {filename} - Class: {item['class']}")

            # Display crop only (optional)
            if show_windows:
                cv2.imshow(f"Crop {i+1} - {item['class']}", crop)

    else:
        print("No detections - try lower confidence")



    if show_windows:
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # Return useful info to the caller (pipeline.py)
    return predictions


# Optional: allow running this file directly for testing
if __name__ == "__main__":
    test_image = "images/red.png"
    preds = run_model_on_image(
        test_image,
        "captured_image",
        show_windows=True,
    )
    print("Predictions:", preds)
