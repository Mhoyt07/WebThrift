from Model import run_model_on_image
from capture import take_photo

def pipeline(image_name="captured_image"):

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
    if predictions:
        print(f"Detected {len(predictions)} items.")
    else:
        print("No items detected.")
    
    return len(predictions)


if __name__ == "__main__":
    pipeline()
