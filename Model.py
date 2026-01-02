import cv2
import numpy as np
from roboflow import Roboflow
from inference_sdk import InferenceHTTPClient 
from dotenv import load_dotenv
from datetime import datetime
from pymongo import MongoClient
import os
import json

load_dotenv()
api_key = os.getenv("API_KEY")

# Load pre-trained clothing detection model (auto-downloads ~6MB)
rf = Roboflow(api_key=api_key)
project = rf.workspace("giangproject").project("clothing-detection-p8vmn")
model = project.version(6).model

# Test your image
image_path = "item003.jpeg"
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
        
        # Save crop
        filename = f"item_{item_num:03d}.jpg"
        cv2.imwrite(filename, crop)
        print(f"Saved: {filename}")
        
        # Display crop only
        cv2.imshow(f'Crop {i+1}', crop)


        detection_data["items"].append({
            "file_path": filename,
            "class": item['class']})
        
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

#prunes part:
client  = MongoClient('mongodb://localhost:27017/')
db = client.clothes_store
clothes = db.clothes

img = cv2.imread(image_path)
cv2.imshow('Original Image', img)

item_id = 0

if results.json()['predictions']:
    for item in results.json()['predictions']:
        document = {
            "ID_no": item_id,
            "date_added": datetime.now(),
            "class": item['class'],
            "image_path": image_path
            }

        clothes.insert_one(document)
        print("Inserted document:", document)


cv2.waitKey(0)
cv2.destroyAllWindows()