import pytest
from db.db_items import init_id_queue, item_insert, check_item, remove_item

def test_item_insert_and_check(clothes_collection, id_queue_collection):
    """
    Checks if item insert and check item work correctly
    """
    init_id_queue(min_id=1, max_id=10, cfg_collection=id_queue_collection)
    
    item_insert(clothes_collection, "T-shirt", "M", "image.jpg", cfg_collection=id_queue_collection)

    assert check_item(clothes_collection, 1) is True
    assert check_item(clothes_collection, 999) is False

def test_remove_item_deletes_existing(clothes_collection, id_queue_collection, capsys):
    """
    Checks if remove item deletes existing items correctly
    """
    init_id_queue(min_id=1, max_id=10, cfg_collection=id_queue_collection)
    
    item_insert(clothes_collection, "Sweater", "L", "sweater.jpg", cfg_collection=id_queue_collection)
    item_insert(clothes_collection, "Jeans", "XL", "jeans.jpg", cfg_collection=id_queue_collection)
    
    assert check_item(clothes_collection, 2) is True

    remove_item(clothes_collection, 2, cfg_collection=id_queue_collection)

    assert check_item(clothes_collection, 2) is False
    out = capsys.readouterr().out
    assert "removed" in out

def test_remove_item_not_found_prints_message(clothes_collection, id_queue_collection, capsys):
    """
    Checks if remove item handles non-existing items properly 
    """
    init_id_queue(min_id=1, max_id=10, cfg_collection=id_queue_collection)
    
    result = remove_item(clothes_collection, 123, cfg_collection=id_queue_collection)

    assert result is False
    out = capsys.readouterr().out
    assert "not found" in out
