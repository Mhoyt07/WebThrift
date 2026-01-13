# conftest.py
import pytest
from pymongo import MongoClient

@pytest.fixture(scope="function")
def mongo_client():
    """Provides a MongoClient connected to localhost."""
    client = MongoClient("mongodb://localhost:27017/")
    yield client
    client.close()


@pytest.fixture(scope="function")
def test_db(mongo_client):
    """Provides a fresh test database for each test function."""
    db = mongo_client.test_clothes_store
    mongo_client.drop_database("test_clothes_store")
    yield db
    mongo_client.drop_database("test_clothes_store") 


@pytest.fixture(scope="function")
def clothes_collection(test_db):
    """Provides the clothes collection for tests."""
    return test_db.clothes


@pytest.fixture(scope="function")
def id_queue_collection(test_db):
    """Provides the ID queue config collection for tests."""
    return test_db.id_queue_config
