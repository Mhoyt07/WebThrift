import cv2
import numpy as np
from roboflow import Roboflow
from inference_sdk import InferenceHTTPClient 
from dotenv import load_dotenv
import os
import json
from collections import Counter

load_dotenv()
api_key = os.getenv("API_KEY")

# Load pre-trained clothing detection model (auto-downloads ~6MB)
rf = Roboflow(api_key=api_key)
project = rf.workspace("giangproject").project("clothing-detection-p8vmn")
model = project.version(6).model

# Test your image
image_path = "red.png"
results = model.predict(image_path, confidence=10, overlap=30)

# Print results
print("Predictions:", results.json())
print(f"Items detected: {len(results.json()['predictions'])}")


# Load + show image
img = cv2.imread(image_path)
cv2.imshow('Original', img)

BASE_COLORS = {
    "red": {"max": (255, 80, 80), "min":(150, 0, 0)}, #creates the ranges for every color
    "green": {"max": (80, 255, 80), "min":(0, 150, 0)},
    "blue": {"max": (80, 80, 255), "min":(0, 0, 150)},
    "yellow": {"max": (255, 255, 80), "min":(150, 150, 0)},
    "orange": {"max": (255, 165, 80), "min":(200, 80, 0)},   
    "purple": {"max": (255, 80, 255), "min":(100, 0, 100)},
    "Pink": {"max": (255, 192, 203), "min":(200, 100, 130)},
    "brown": {"max": (210, 180, 140), "min":(50, 30, 20)},
    "gray": {"max": (180, 180, 180), "min":(70, 70, 70)},
    "black": {"min": (0, 0, 0), "max": (50, 50, 50)},
    "white": {"min": (200, 200, 200), "max": (255, 255, 255)},
}

def pixel_color(rgb): #assigns a pixel to a color based on the min and max
    r, g, b = rgb
    for color_name, bounds in BASE_COLORS.items():
        min_r, min_g, min_b = bounds["min"]
        max_r, max_g, max_b = bounds["max"]

        if (min_r <= r <= max_r) and (min_g <= g <= max_g) and (min_b <= b <= max_b):
            return color_name

def dominant_color(image): #finds the dominant color in the cropped image
    height, width = image.shape[:2]

    color_counts = Counter()

    for y in range(height):
        for x in range(width):
            bgr = image[y, x]
            rgb = (int(bgr[2]), int(bgr[1]), int(bgr[0]))  # Converting the stupid BGR to RGB
            color_name = pixel_color(rgb)
            if color_name:
                color_counts[color_name] += 1
        
    if color_counts:
        return color_counts.most_common(1)[0][0]
    else:
        return "unknown"

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

        #from abhi code to test
        crop = img[y:y+h, x:x+w]
        #crop = img[y:y2, x:x2]

        # Gets dominant color
        dom_color = dominant_color(crop)

        
        # Save crop
        filename = f"item_{item_num:03d}.jpg"
        cv2.imwrite(filename, crop)
        print(f"Saved: {filename} - Class: {item['class']}")
        
        print(f"Dominant Color: {dom_color}")
        # Display crop only
        cv2.imshow(f"Crop {i+1} - {item['class']}", crop)

        detection_data["items"].append({
            "file_path": filename,
            "class": item['class'],
            "color": dom_color
            
        })
        item_num += 1  # Increment for next detection
        
else:
    print("No detections - try lower confidence")
# Add this to your existing code (after crop creation loop)

# Load baseline
data_path = "data.json"
items = {}
# Load existing data
if os.path.exists(data_path):
    with open(data_path, 'r') as f:
        json_data = json.load(f)
else:
    json_data = {"items": []}

# Append NEW items only
new_items = [item for item in detection_data["items"] if item['file_path'] not in [existing_item['file_path'] for existing_item in data["items"]]]
data["items"].extend(new_items)


# Save (keeps old + adds new)
with open(data_path, 'w') as f:
    json.dump(data, f, indent=2)


cv2.waitKey(0)
cv2.destroyAllWindows()