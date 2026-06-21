# camera/capture.py
# Uses rpicam via subprocess for new Bookworm OS

import cv2
import numpy as np
import subprocess
import threading
import time
import os


class CameraCapture:
    def __init__(self, width=640, height=480):
        self.width   = width
        self.height  = height
        self.frame   = None
        self.running = False
        self._lock   = threading.Lock()
        self._start()

    def _start(self):
        try:
            # Try picamera2 first
            from picamera2 import Picamera2
            self.picam2 = Picamera2()
            config = self.picam2.create_preview_configuration(
                main={
                    "size":   (self.width, self.height),
                    "format": "RGB888"
                }
            )
            self.picam2.configure(config)
            self.picam2.start()
            self.method = "picamera2"
            time.sleep(2)
            print(f"Camera ready via picamera2: "
                  f"{self.width}x{self.height}")

        except Exception as e:
            print(f"picamera2 failed: {e}")
            print("Trying OpenCV fallback...")
            self.picam2 = None

            # Try OpenCV with libcamera
            try:
                self.cap = cv2.VideoCapture(
                    0, cv2.CAP_V4L2)
                self.cap.set(
                    cv2.CAP_PROP_FRAME_WIDTH,
                    self.width)
                self.cap.set(
                    cv2.CAP_PROP_FRAME_HEIGHT,
                    self.height)
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.method = "opencv"
                    print(f"Camera ready via OpenCV: "
                          f"{self.width}x{self.height}")
                else:
                    raise Exception("OpenCV read failed")

            except Exception as e2:
                print(f"OpenCV failed: {e2}")
                self.cap = None
                self.method = None
                print("No camera available")

    def read_frame(self):
        try:
            if self.method == "picamera2":
                frame = self.picam2.capture_array()
                frame = cv2.cvtColor(
                    frame, cv2.COLOR_RGB2BGR)
                return frame

            elif self.method == "opencv":
                ret, frame = self.cap.read()
                if ret:
                    return frame
                return None

            else:
                return None

        except Exception as e:
            print(f"Frame capture error: {e}")
            return None

    def release(self):
        try:
            if self.method == "picamera2" \
                    and self.picam2:
                self.picam2.stop()
            elif self.method == "opencv" \
                    and self.cap:
                self.cap.release()
            print("Camera released")
        except Exception as e:
            print(f"Release error: {e}")
# ─────────────────────────────────────────────
# STANDALONE TEST
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import cv2
    import time

    print("\n" + "="*50)
    print("CAMERA TEST")
    print("="*50)

    print("Initializing camera...")
    cam = CameraCapture()
    time.sleep(2)

    print("Capturing 3 frames...")
    for i in range(3):
        frame = cam.read_frame()
        if frame is not None:
            print(f"✓ Frame {i+1}: "
                  f"shape={frame.shape} "
                  f"dtype={frame.dtype}")
            # Save test image
            os.makedirs('data', exist_ok=True)
            save_path = f"data/camera_test_{i+1}.jpg"
            cv2.imwrite(save_path, frame)
            print(f"  Saved: {save_path}")
        else:
            print(f"✗ Frame {i+1}: FAILED — camera returned None")
        time.sleep(0.5)

    cam.release()
    print("\n" + "="*50)
    print("Camera test complete")
    print("="*50 + "\n")
