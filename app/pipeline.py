from ml.model import run_model_on_image
from db.db_items import get_next_id, get_default_collection, item_insert


# wsg pull request, this change to function param is for testing
def pipeline(image_name="captured_image", image_path=None, db_name=None, predictions=None):

    # Defaults insert success to False
    insert_success = False

    # Step 1: Capture photo from ESP32-CAM
    # double wsg pull request, this is for testing with existing images rather than camera cuz fuh camera
    if image_path == None:
        from camera.capture import take_photo
        image_path = take_photo(image_name)

    # Step 2: Run model on captured image
    if predictions is None:    
        predictions = run_model_on_image(
            image_path,
            image_name,
            confidence=10,
            overlap=30,
            show_windows=False,
        )
    

    # Step 3: Process predictions as needed
    if len(predictions) == 1:
        clothes = get_default_collection(db=db_name)
        # Getting item class
        item_class = predictions[0]['class']

        # Insert item into database
        insert_success = item_insert(clothes, item_class, "M", image_path)

    elif len(predictions) > 1:
        print(f"{predictions} items detected.")

    else:
        print("No items detected.")
    
    return len(predictions), insert_success


if __name__ == "__main__":
    pipeline()
