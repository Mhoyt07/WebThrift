import pytest
from ml.model import run_model_on_image

# For adding future tests, just add more tuples to the list below
@pytest.mark.parametrize(
    "image_path, expected_classes",
    [
        ("images/item003.jpeg", ["t-shirt", "shirt"]),
    ]
)
def test_model_clothing_classification(image_path, expected_classes, test_db):
    """
    Tests if the Roboflow model can correctly classify clothing items for each item in the tuple
    """
    predictions = run_model_on_image(
        image_path=image_path,
        image_name="test_image",
        confidence=10,
        overlap=30,
    )
    # model tests
    assert len(predictions) >= 1, "No detections returned by Roboflow"

    detected_classes = [p["class"].lower() for p in predictions]

    assert any(cls in detected_classes for cls in expected_classes), (
        f"Expected one of {expected_classes}, "
        f"but got {detected_classes}"
    )
    assert predictions[0]['confidence'] >= 0.4
    