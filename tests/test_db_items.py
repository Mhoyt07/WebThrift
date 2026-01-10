# test_db_items.py
from db.db_items import item_insert, check_item, remove_item


def test_item_insert_and_check(clothes_collection):
    item_insert(clothes_collection, 1, "T-shirt", "M", "image.jpg")

    assert check_item(clothes_collection, 1) is True
    assert check_item(clothes_collection, 999) is False


def test_remove_item_deletes_existing(clothes_collection, capsys):
    item_insert(clothes_collection, 2, "Sweater", "L", "sweater.jpg")
    assert check_item(clothes_collection, 2) is True

    remove_item(clothes_collection, 2)

    assert check_item(clothes_collection, 2) is False
    out = capsys.readouterr().out
    assert "removed successfully" in out


def test_remove_item_not_found_prints_message(clothes_collection, capsys):
    remove_item(clothes_collection, 123)

    out = capsys.readouterr().out
    assert "not found" in out
