from datetime import datetime
from pymongo import MongoClient 

def get_default_collection(): 
    """
    Connect to the MongoDB server and return the default 'clothes' collection.
    """
    client = MongoClient('mongodb://localhost:27017/')
    db = client.clothes_store
    return db.clothes

def ensure_unique_id_index():
    """
    Ensure that the 'ID_no' field in the clothes collection has a unique index.
    """
    clothes = get_default_collection()
    clothes.create_index("ID_no", unique=True)

def init_db_system():
    """
    Initialize the database system by setting up the ID queue.
    """
    ensure_unique_id_index()
    init_id_queue()


def get_id_queue_collection():
    """
    Return the collection that stores the ID queue configuration document.
    """
    client = MongoClient('mongodb://localhost:27017/')
    db = client.clothes_store
    return db.id_queue_config

def init_id_queue(min_id=1, max_id=999999):
    """
    Initialize the circular ID queue configuration document if it doesn't exist.
    """
    cfg = get_id_queue_collection()
    cfg.update_one(
        {"_id": "id_queue"},
        {
            "$setOnInsert": {
                "min_id": min_id,
                "max_id": max_id,
                "next_id": min_id,
            }
        },
        upsert=True,
    )

def get_next_id(clothes, max_tries=None):
    """
    Docstring for get_next_id
    
    :param clothes: Clothes collection object.
    :param max_tries: Safety bound to avoid infinite loops. Defaults to max possible unique IDS. Specify to override.
    :return: Next available unique ID_no.
    :raises RuntimeError: If no unused ID is found after max_tries.
    """
    cfd_coll = get_id_queue_collection()
    cfg = cfd_coll.find_one({"_id": "id_queue"})
    if cfg is None:
        raise RuntimeError("ID queue not initialized; call init_db_system() first.")

    current = cfg["next_id"]
    min_id = cfg["min_id"]
    max_id = cfg["max_id"]

    if max_tries is None:
        max_tries = max_id - min_id + 1

    chosen_id = None
    found = False
    tries = 0

    while tries < max_tries and not found:
        if not check_item(clothes, current):
            # Found an unused ID
            new_next_id = current + 1
            if new_next_id > max_id:
                new_next_id = min_id

            cfd_coll.update_one(
                {"_id": "id_queue"},
                {"$set": {"next_id": new_next_id}}
            )
            chosen_id = current
            found = True
        else:
            # ID already in use, try next
            current += 1
            if current > max_id:
                current = min_id
            tries += 1
    if not found:
        raise RuntimeError("Could not find an unused ID after max tries.")
    return chosen_id


def item_insert(clothes, class_name, size, image_path):
    """
    Docstring for item_insert
    
    :param clothes: Clothes collection object.
    :param ID_no: Unique ID associated with a clothing item.
    :param class_name: Clothing classification (e.g., shirt, pants).
    :param size: Size of clothing item.
    :param image_path: Path to the image file.
    :return: Boolean indicating success or failure.
    :raises RuntimeError: If the ID queue is not initialized.
    """
    
    cfg_coll = get_id_queue_collection()
    cfg = cfg_coll.find_one({"_id": "id_queue"})
    if cfg is None:
        raise RuntimeError("ID queue not initialized; call init_db_system() first.")
    
    ID_no = get_next_id(clothes)
    
    result = clothes.insert_one({
        "ID_no": ID_no,
        "date_added": datetime.now(),
        "class": class_name,
        "size": size,
        "image_path": image_path
    })
    
    
    return result.acknowledged

def check_item(clothes, ID_no):
    """
    Check if an item with the given ID_no exists in the collection.
    
    :param ID_no: Unique ID associated with a clothing item.
    """
    item = clothes.find_one({"ID_no": ID_no})
    return item is not None

def remove_item(clothes, ID_no):
    """
    Remove an item from the clothes collection.

    :param clothes: Clothes collection object.
    :param ID_no: Unique ID associated with a clothing item.
    :raises RuntimeError: If the ID queue is not initialized.
    """
    # 1️⃣ Ensure the ID queue is initialized
    cfg_coll = get_id_queue_collection()
    cfg = cfg_coll.find_one({"_id": "id_queue"})
    if cfg is None:
        raise RuntimeError("ID queue not initialized; cannot remove item safely.")

    # 2️⃣ Attempt to delete the item
    result = clothes.delete_one({"ID_no": ID_no})

    if not result.acknowledged:
        raise RuntimeError("Delete was not acknowledged by MongoDB.")

    if result.deleted_count == 0:
        # Item did not exist
        print(f"Item {ID_no} not found.")
        return False
    if result.deleted_count > 0:
        print(f"Item {ID_no} removed.")
        return True