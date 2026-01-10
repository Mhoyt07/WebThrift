from datetime import datetime
from pymongo import MongoClient 

def get_default_collection(): 
    """
    Connect to the MongoDB server and return the default 'clothes' collection.
    """
    client = MongoClient('mongodb://localhost:27017/')
    db = client.clothes_store
    return db.clothes


def item_insert(clothes, ID_no, class_name, size, image_path):
    """
    Docstring for item_insert
    
    :param clothes: Clothes collection object.
    :param ID_no: Unique ID associated with a clothing item.
    :param class_name: Clothing classification (e.g., shirt, pants).
    :param size: Size of clothing item.
    :param image_path: Path to the image file.
    """
    clothes.insert_one({
        "ID_no": ID_no,
        "date_added": datetime.now(),
        "class": class_name,
        "size": size,
        "image_path": image_path
    })
    
    
    print(f"Item {ID_no} inserted successfully.")

def check_item(clothes, ID_no):
    """
    Check if an item with the given ID_no exists in the collection.
    
    :param ID_no: Unique ID associated with a clothing item.
    """
    item = clothes.find_one({"ID_no": ID_no})
    return item is not None

def remove_item(clothes, ID_no):
    """
    Remove an item with the given ID_no from the collection.
    
    :param ID_no: Unique ID associated with a clothing item.
    """
    result = clothes.delete_one({"ID_no": ID_no})
    
    if not result.acknowledged:
        raise RuntimeError("Delete was not acknowledged by MongoDB")
    
    if result.deleted_count > 0:
        print(f"Item {ID_no} removed successfully.")
    else:
        print(f"Item {ID_no} not found.")

