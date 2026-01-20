import pytest
from app.pipeline import pipeline


@pytest.mark.parametrize(
    "image_path, expected_classes",
    [
        ("images/item003.jpeg", ["t-shirt", "shirt"]),
    ]
)
def test_pipeline(test_db, image_path, expected_classes):
    """
    Tests pipeline function without using the camera with tuple data
    """
    count, insert_success = pipeline(
        image_name="test_image",
        image_path=image_path,
        db_name=test_db,
    )

    assert count == 1
    assert insert_success is True

    inserted_item = test_db.clothes.find_one({})
    assert inserted_item is not None
    assert inserted_item["class"].lower() in expected_classes
    assert inserted_item["size"] == "M"
    assert inserted_item["image_path"] == image_path
