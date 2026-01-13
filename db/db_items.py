from datetime import datetime
from pymongo import MongoClient

def get_default_collection(db=None):
    """
    Connect to the MongoDB server and return the default 'clothes' collection.
    If db is provided, use that database (for testing).
    """
    if db is None:
        client = MongoClient('mongodb://localhost:27017/')
        db = client.clothes_store
    return db.clothes

def get_id_queue_collection(db=None):
    """
    Return the collection that stores the ID queue configuration document.
    If db is provided, use that database (for testing).
    """
    if db is None:
        client = MongoClient('mongodb://localhost:27017/')
        db = client.clothes_store
    return db.id_queue_config


def init_id_queue(min_id=1, max_id=999999, cfg_collection=None):
    """
    Initialize the circular ID queue configuration document if it doesn't exist.
    :param min_id: Minimum ID in the queue.
    :param max_id: Maximum ID in the queue.
    :param cfg_collection: ID queue configuration collection, leave empty to use default.
    """
    if cfg_collection is None:
        cfg_collection = get_id_queue_collection()
    cfg_collection.update_one(
        {"_id": "id_queue"},
        {"$setOnInsert": {"min_id": min_id, "max_id": max_id, "next_id": min_id}},
        upsert=True
    )

def get_next_id(clothes, max_tries=None, cfg_collection=None):
    """
    Get the next available ID from the queue.
    :param clothes: Clothes collection object.
    :param max_tries: Maximum number of attempts to find an unused ID.
    :param cfg_collection: ID queue configuration collection, leave empty to use default.
    """
    if cfg_collection is None:
        cfg_collection = get_id_queue_collection()

    cfg = cfg_collection.find_one({"_id": "id_queue"})
    if cfg is None:
        raise RuntimeError("ID queue not initialized; call init_id_queue() first.")

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
            # ID unused
            new_next_id = current + 1
            if new_next_id > max_id:
                new_next_id = min_id

            cfg_collection.update_one(
                {"_id": "id_queue"},
                {"$set": {"next_id": new_next_id}}
            )
            chosen_id = current
            found = True
        else:
            current += 1
            if current > max_id:
                current = min_id
            tries += 1

    if not found:
        raise RuntimeError("Could not find an unused ID after max tries.")

    return chosen_id

def item_insert(clothes, class_name, size, image_path, cfg_collection=None):
    """
    Insert a clothing item. Returns True if successful.
    :param clothes: Clothes collection object.
    :param class_name: Clothing classification (e.g., shirt, pants).
    :param size: Size of clothing 
    :param image_path: Path to the image file.
    :param cfg_collection: ID queue configuration collection, leave empty to use default.
    """
    if cfg_collection is None:
        cfg_collection = get_id_queue_collection()
    
    ID_no = get_next_id(clothes, cfg_collection=cfg_collection)

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
    return clothes.find_one({"ID_no": ID_no}) is not None

def remove_item(clothes, ID_no, cfg_collection=None):
    """
    Remove an item from the collection. Returns True if removed, False if not found.
    :param clothes : Clothes collection object.
    :param ID_no: Unique ID associated with a clothing item.
    :param cfg_collection: ID queue configuration collection, leave empty to use default.
    """
    if cfg_collection is None:
        cfg_collection = get_id_queue_collection()

    cfg = cfg_collection.find_one({"_id": "id_queue"})
    if cfg is None:
        raise RuntimeError("ID queue not initialized; cannot remove item safely.")

    result = clothes.delete_one({"ID_no": ID_no})

    if not result.acknowledged:
        raise RuntimeError("Delete was not acknowledged by MongoDB.")

    if result.deleted_count == 0:
        print(f"Item {ID_no} not found.")
        return False

    print(f"Item {ID_no} removed.")
    return True
