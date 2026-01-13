import pytest
from db.db_items import init_id_queue, get_next_id, check_item

def test_init_id_queue_creates_config(id_queue_collection):
    init_id_queue(min_id=10, max_id=12, cfg_collection=id_queue_collection)

    cfg = id_queue_collection.find_one({"_id": "id_queue"})
    assert cfg is not None
    assert cfg["min_id"] == 10
    assert cfg["max_id"] == 12
    assert cfg["next_id"] == 10


def test_get_next_id_returns_first_available(clothes_collection, id_queue_collection):
    init_id_queue(min_id=1, max_id=5, cfg_collection=id_queue_collection)

    next_id1 = get_next_id(clothes_collection, cfg_collection=id_queue_collection)
    next_id2 = get_next_id(clothes_collection, cfg_collection=id_queue_collection)
    next_id3 = get_next_id(clothes_collection, cfg_collection=id_queue_collection)
    next_id4 = get_next_id(clothes_collection, cfg_collection=id_queue_collection)
    next_id5 = get_next_id(clothes_collection, cfg_collection=id_queue_collection)
    
    assert next_id1 == 1
    assert next_id2 == 2
    assert next_id3 == 3
    assert next_id4 == 4
    assert next_id5 == 5


def test_get_next_id_skips_existing_ids(clothes_collection, id_queue_collection):
    init_id_queue(min_id=1, max_id=5, cfg_collection=id_queue_collection)

    clothes_collection.insert_one({"ID_no": 1})
    clothes_collection.insert_one({"ID_no": 2})
    clothes_collection.insert_one({"ID_no": 4})

    next_id = get_next_id(clothes_collection, cfg_collection=id_queue_collection)
    next_id2 = get_next_id(clothes_collection, cfg_collection=id_queue_collection)

    assert next_id == 3
    assert next_id2 == 5


def test_get_next_id_raises_when_all_ids_used(clothes_collection, id_queue_collection):
    init_id_queue(min_id=1, max_id=2, cfg_collection=id_queue_collection)

    clothes_collection.insert_many([
        {"ID_no": 1},
        {"ID_no": 2},
    ])

    with pytest.raises(RuntimeError):
        get_next_id(clothes_collection, cfg_collection=id_queue_collection)

# checks if the queue works circularly after deletions
def test_get_next_id_circular_wraparound(clothes_collection, id_queue_collection):
    init_id_queue(min_id=1, max_id=3, cfg_collection=id_queue_collection)
    
    clothes_collection.insert_one({"ID_no": 1})
    clothes_collection.insert_one({"ID_no": 2})
    clothes_collection.insert_one({"ID_no": 3})
    
    clothes_collection.delete_one({"ID_no": 2})
    next_id = get_next_id(clothes_collection, cfg_collection=id_queue_collection)
    assert next_id == 2
