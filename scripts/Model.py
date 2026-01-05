import cv2
import numpy as np
from roboflow import Roboflow
from inference_sdk import InferenceHTTPClient 
from dotenv import load_dotenv
import os
import json

load_dotenv()
api_key = os.getenv("API_KEY")

# Load pre-trained clothing detection model (auto-downloads ~6MB)
rf = Roboflow(api_key=api_key)
project = rf.workspace("giangproject").project("clothing-detection-p8vmn")
model = project.version(6).model

# Test your image
image_path = "images/red.png"
results = model.predict(image_path, confidence=10, overlap=30)

# Print results
print("Predictions:", results.json())
print(f"Items detected: {len(results.json()['predictions'])}")


# Load + show image
img = cv2.imread(image_path)
cv2.imshow('Original', img)

# Load existing data
data_path = "data.json"
if os.path.exists(data_path):
    with open(data_path, 'r') as f:
        data = json.load(f)
else:
    data = {"items": []}

detection_data = {"items": []}
item_num = len(data["items"]) + 1


if results.json()['predictions']:
    predictions = results.json()['predictions']
    
    # Crop each item (no boxes/labels)
    for i, item in enumerate(predictions):
        # Calculate coordinates
        x = int(item['x'] - item['width'] / 2)
        y = int(item['y'] - item['height'] / 2)
        w = int(item['width'])
        h = int(item['height'])
        
        # Skip if too small (less than 50x50 pixels)
        if w < 50 or h < 50:
            print(f"Skipping detection {i+1}: too small ({w}x{h})")
            continue
        
        # Add boundary checking
        x = max(0, x)
        y = max(0, y)
        x2 = min(img.shape[1], x + w)
        y2 = min(img.shape[0], y + h)
        
        # Just crop - no drawing
        crop = img[y:y2, x:x2]
        
        # Save crop
        filename = f"images/item_{item_num:03d}.jpg"
        cv2.imwrite(filename, crop)
        print(f"Saved: {filename} - Class: {item['class']}")
        
        # Display crop only
        cv2.imshow(f"Crop {i+1} - {item['class']}", crop)

        detection_data["items"].append({
            "file_path": filename,
            "class": item['class']
        })
        
        item_num += 1  # Increment for next detection
        
else:
    print("No detections - try lower confidence")


# Append NEW items only
new_items = [item for item in detection_data["items"] if item['file_path'] not in [existing_item['file_path'] for existing_item in data["items"]]]
data["items"].extend(new_items)


# Save (keeps old + adds new)
with open(data_path, 'w') as f:
    json.dump(data, f, indent=2)


cv2.waitKey(0)
cv2.destroyAllWindows()