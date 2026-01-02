from datetime import datetime
from pymongo import MongoClient 


client = MongoClient('mongodb://localhost:27017/')

db = client.clothes_store

clothes = db.clothes

clothes.insert_one({
    "ID_no": 0,
    "date_added": datetime.now(),
    "class": "Long Sleeve T-shirt",
    "color": "Green",
    "size": "L",
    "image_path": "PruneGreenSweater.jpeg"
    
})