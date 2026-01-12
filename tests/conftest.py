import pytest
from pymongo import MongoClient

@pytest.fixture
def mongo_client():
    """
    Provide a MongoDB client for tests.
    """
    client = MongoClient("mongodb://localhost:27017/")
    yield client
    client.close()


@pytest.fixture
def clothes_collection(mongo_client):
    """
    Provide a fresh clothes collection for each test.
    """
    db = mongo_client["clothes_store"]
    collection = db["clothes"]

    # Ensure clean state
    collection.delete_many({})

    yield collection

    # Cleanup
    collection.delete_many({})


@pytest.fixture
def id_queue_collection(mongo_client):
    """
    Provide a fresh ID queue config collection for each test.
    """
    db = mongo_client["clothes_store"]
    collection = db["id_queue_config"]

    # Ensure clean state
    collection.delete_many({})

    yield collection

    # Cleanup
    collection.delete_many({})
