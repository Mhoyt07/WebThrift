import os
import cv2
import pytest 
from ml.model import run_model_on_image

# For adding future tests, just add more tuples to the list below
@pytest.mark.parametrize(
    "image_path, expected_classes",
    [
        ("images/test_item001.jpeg", ["shirt"]),
        #("images/test_item002.jpeg", ["shirt"]),
        #("images/test_item003.jpeg", ["t-shirt"]),
        #("images/test_item004.jpeg", ["sweater", "shirt", "long sleeve"]),
    ]
)
def test_model_clothing_classification(image_path, expected_classes, test_db):
    """
    Tests if the Roboflow model can correctly classify clothing items for each item in the tuple
    """
    predictions, crop_info = run_model_on_image(
        image_path=image_path,
        image_name="test_image",
        confidence=10,
        overlap=30,
    )
    # model tests
    assert len(predictions) == 1, "No more/less than 1 item returned by Roboflow"

    detected_classes = [p["class"].lower() for p in predictions]

    assert any(cls in detected_classes for cls in expected_classes), (
        f"Expected one of {expected_classes}, "
        f"but got {detected_classes}"
    )
    assert predictions[0]['confidence'] >= 0.4
    
    # crop tests
    assert os.path.exists(crop_info['filepath']), "Crop file DNE"
        
    assert crop_info['width'] >= 50, "width too small"  #change this value
    assert crop_info['height'] >= 50, "height too small" #change this value
    
    aspect_ratio = crop_info["width"] / crop_info["height"]
    
    assert 0.2 <= aspect_ratio <= 5.0 , "aspect ratio not in reasonable bounds"
        
    
    