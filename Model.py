import cv2
import numpy as np
from roboflow import Roboflow
from inference_sdk import InferenceHTTPClient 
from dotenv import load_dotenv
import os
import json
from collections import Counter

def get_dom_color(crop):
    small_crop = cv2.resize(crop, (50, 50)) #crop resize
    small_crop = cv2.cvtColor(small_crop, cv2.COLOR_BGR2RGB) #convert to RGB
    pixels = small_crop.reshape(-1, 3) #reshape to list of pixels

    counts = Counter([tuple(pixel) for pixel in pixels]) #finds most common
    dominant = counts.most_common(1)[0][0]
    return dominant







load_dotenv()
api_key = os.getenv("API_KEY")

# Load pre-trained clothing detection model (auto-downloads ~6MB)
rf = Roboflow(api_key=api_key)
project = rf.workspace("giangproject").project("clothing-detection-p8vmn")
model = project.version(6).model

# Test your image
image_path = "red.jpeg"
results = model.predict(image_path, confidence=10, overlap=30)

# Print results
print("Predictions:", results.json())
print(f"Items detected: {len(results.json()['predictions'])}")


# Load + show image
img = cv2.imread(image_path)
cv2.imshow('Original', img)
detection_data = {"items": []}
with open("data.json", 'r') as f:
    data = json.load(f)

item_num = len(data["items"]) + 1

if results.json()['predictions']:
    predictions = results.json()['predictions']
    
    # Crop each item (no boxes/labels)
    for i, item in enumerate(predictions):
        x = int(item['x'] - item['width'] / 2)
        y = int(item['y'] - item['height'] / 2)
        w = int(item['width'])
        h = int(item['height'])
        
        # Just crop - no drawing
        crop = img[y:y+h, x:x+w]


        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv) #split h s v channels

        mask = (s > 50) & (v < 230)

        # If mask removed too much, fallback to whole crop
        if np.count_nonzero(mask) < 100:
            mask = np.ones_like(s, dtype=bool)


        h_mean = int(np.mean(h[mask]))
        s_mean = int(np.mean(s[mask]))
        v_mean = int(np.mean(v[mask]))

        # Convert HSV average to color name
        if s_mean < 40 and v_mean > 200:
            color_name = "white"
        elif h_mean < 10 or h_mean > 160:
            color_name = "red"
        elif 10 <= h_mean < 25:
            color_name = "orange"
        elif 25 <= h_mean < 35:
            color_name = "yellow"
        elif 35 <= h_mean < 85:
            color_name = "green"
        elif 85 <= h_mean < 130:
            color_name = "blue"
        elif 130 <= h_mean < 160:
            color_name = "purple"
        elif s_mean < 40 and v_mean < 100:
            color_name = "black"
        else:
            color_name = "unknown"

        print("Detected color:", color_name)


        avg_color_per_row = np.average(crop, axis=0) #avg per row
        avg_color = np.average(avg_color_per_row, axis=0)

        avg_color = tuple(map(int, avg_color))


        print(f"Detected color: {color_name}")
        
        # Save crop
        filename = f"item_{item_num:03d}.jpg"
        cv2.imwrite(filename, crop)
        print(f"Saved: {filename}")
        
        # Display crop only
        cv2.imshow(f'Crop {i+1}', crop)


        detection_data["items"].append({
            "file_path": filename,
            "class": item['class'], "color": color_name,})
        
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
new_items = [item for item in detection_data["items"] if item['file_path'] not in [existing_item['file_path'] for existing_item in json_data["items"]]]
json_data["items"].extend(new_items)

# Save (keeps old + adds new)
with open(data_path, 'w') as f:
    json.dump(json_data, f)



cv2.waitKey(0)
cv2.destroyAllWindows()