from datetime import datetime
from pymongo import MongoClient 

def get_default_collection(): 
    client = MongoClient('mongodb://localhost:27017/')
    db = client.clothes_store
    return db.clothes


def item_insert(clothes, ID_no, class_name, size, image_path):
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
    
    :param ID_no: ID associated with a clothing item.
    """
    item = clothes.find_one({"ID_no": ID_no})
    return item is not None

def remove_item(clothes, ID_no):
    """
    Remove an item with the given ID_no from the collection.
    
    :param ID_no: ID associated with a clothing item.
    """
    result = clothes.delete_one({"ID_no": ID_no})
    
    if not result.acknowledged:
        raise RuntimeError("Delete was not acknowledged by MongoDB")
    
    if result.deleted_count > 0:
        print(f"Item {ID_no} removed successfully.")
    else:
        print(f"Item {ID_no} not found.")

