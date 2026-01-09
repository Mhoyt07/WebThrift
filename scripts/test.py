from datetime import datetime
from pymongo import MongoClient 


client = MongoClient('mongodb://localhost:27017/')

db = client.clothes_store

clothes = db.clothes

clothes.insert_one({
    "ID_no": 0,
    "date_added": datetime.now(),
    "class": "Long Sleeve T-shirt",
    "size": "L",
    "image_path": "PruneGreenSweater.jpeg"
    
})

def item_insert(ID_no, class_name, size, image_path):
    clothes.insert_one({
        "ID_no": ID_no,
        "date_added": datetime.now(),
        "class": class_name,
        "size": size,
        "image_path": image_path
    })
    
    
    print(f"Item {ID_no} inserted successfully.")

def item_query(ID_no):
    item = clothes.find_one({"ID_no": ID_no})
    if item:
        print(f"Item found: {item}")
    else:
        print(f"No item found with ID_no: {ID_no}")
