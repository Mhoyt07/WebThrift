from ml.model import run_model_on_image
from camera.capture import take_photo
from db.db_items import get_next_id, get_default_collection, item_insert



def pipeline(image_name="captured_image"):

    # Defaults insert success to False
    insert_success = False

    # Step 1: Capture photo from ESP32-CAM
    image_path = take_photo(image_name)

    # Step 2: Run model on captured image
    predictions = run_model_on_image(
        image_path,
        image_name,
        confidence=10,
        overlap=30,
        show_windows=False,
    )

    # Step 3: Process predictions as needed
    if len(predictions) == 1:
        clothes = get_default_collection()
        # Get next available ID 
        ID_no = get_next_id(clothes)

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
