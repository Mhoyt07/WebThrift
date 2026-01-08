import serial
import time
from pathlib import Path

PORT = '/dev/cu.usbserial-2110'   # <- your ESP32-CAM USB serial device
BAUD = 115200
TIMEOUT = 10

def take_photo(image_name):
    ser = serial.Serial(PORT, BAUD, timeout=TIMEOUT)
    time.sleep(2)  # let ESP32 boot

    # Clear any old junk
    ser.reset_input_buffer()
    ser.reset_output_buffer()

    print("Sending CAPTURE...")
    ser.write(b"CAPTURE\n")
    ser.flush()

    # ---- 1. Wait for header 0xAA 0x55 ----
    print("Waiting for header 0xAA 0x55...")
    while True:
        b1 = ser.read(1)
        if not b1:
            raise RuntimeError("Timeout waiting for first header byte")
        if b1[0] == 0xAA:
            b2 = ser.read(1)
            if not b2:
                raise RuntimeError("Timeout waiting for second header byte")
            if b2[0] == 0x55:
                break  # header found

    # ---- 2. Read 4‑byte length (little endian) ----
    len_bytes = ser.read(4)
    if len(len_bytes) != 4:
        raise RuntimeError("Timeout reading length bytes")

    img_len = int.from_bytes(len_bytes, 'little')
    print(f"Image length: {img_len} bytes")

    # ---- 3. Read JPEG bytes ----
    img_data = bytearray()
    while len(img_data) < img_len:
        chunk = ser.read(img_len - len(img_data))
        if not chunk:
            # no more data before reaching expected length
            break
        img_data.extend(chunk)
        print(f"\rReceived {len(img_data)}/{img_len} bytes", end="", flush=True)
    print()

    if len(img_data) != img_len:
        raise RuntimeError(f"Short read: expected {img_len}, got {len(img_data)}")

    # ---- 4. Save to file ----
    # Directory of this script
    BASE_DIR = Path(__file__).resolve().parent

    # images/ subfolder next to the script
    out_path = BASE_DIR.parent / "images" / f"{image_name}.jpg"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    out_path.write_bytes(img_data)
    print(f"Saved {out_path}")

    ser.close()

    return str(out_path)

if __name__ == "__main__":
    print("Image Path:" , take_photo("photo"))