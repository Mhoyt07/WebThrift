import serial
from pipeline import pipeline
from db.db_items import init_db_system
import time

def main():

    # Initialize the database system
    init_db_system()

    PORT = '/dev/cu.usbmodem211401'  # <- your ESP32-CAM USB serial device

    # Configure serial connection
    ser = serial.Serial(PORT, 115200, timeout=1)
    ser.flush()

    blink_time = 0.25 # seconds
    def blink_led(num):
        # Single blink for items detected
            ser.write(f"led{num}_on\n".encode('utf-8'))
            time.sleep(blink_time)
            ser.write(f"led{num}_off\n".encode('utf-8'))
            time.sleep(blink_time)

    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                if line == "start":
                    print("Starting pipeline...")
                    items, insert_success = pipeline()
                    items = -1 if items == 0 else items
            if items > 0:
                # Single blink for items detected
                blink_led(1)
                items = 0
            elif items == -1:
                # Double blink for no items detected
                blink_led(1)
                blink_led(1)
                items = 0
            
            # Blink led 2 to say if an item was inserted into db successfully
            if insert_success:
                blink_led(2)
            else:
                blink_led(2)
                blink_led(2)
    ser.close()
            
if __name__ == "__main__":
    main()