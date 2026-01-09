import pytest
from pymongo import MongoClient

@pytest.fixture
def clothes_collection():
    """
    Provide a fresh test collection for each test and clean it up after.
    """
    client = MongoClient("mongodb://localhost:27017/")
    db = client["clothes_store_test"]
    collection = db["clothes"]

    # Ensure it's empty before each test
    collection.delete_many({})

    yield collection

    # Cleanup after each test
    collection.delete_many({})
