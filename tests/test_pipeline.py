import pytest
from app.pipeline import pipeline

# For adding future tests, just add more tuples to the list below
@pytest.mark.parametrize(
    "image_path, test_predictions, expected_classes, expected_sizes",
    [
        ("images/test_item001.jpeg", [{"class": "shirt", "size": "M", "image_path": "images/test_item001.jpeg"}], "shirt", "M"),
        ("images/test_item002.jpeg", [{"class": "shirt", "size": "M", "image_path": "images/test_item002.jpeg"}], "shirt", "M"),
        ("images/test_item003.jpeg", [{"class": "t-shirt", "size": "M", "image_path": "images/test_item003.jpeg"}], "t-shirt", "M"),
        ("images/test_item004.jpeg", [{"class": "sweater", "size": "M", "image_path": "images/test_item004.jpeg"}], "sweater", "M"),
        
    ]
)
def test_pipeline(test_db, image_path, expected_classes, expected_sizes, test_predictions):
    """
    Tests pipeline function without using the camera or model with tuple data
    Verifies that it inserts properly into the database
    """
    count, insert_success = pipeline(
        image_name="test_image",
        image_path=image_path,
        db_name=test_db,
        predictions=test_predictions        
    )

    assert count == 1
    assert insert_success is True

    inserted_item = test_db.clothes.find_one({})
    assert inserted_item is not None
    assert inserted_item["class"].lower() in expected_classes
    assert inserted_item["size"] == expected_sizes 
    assert inserted_item["image_path"] == image_path
