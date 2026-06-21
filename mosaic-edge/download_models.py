from deepface import DeepFace
import numpy as np
import cv2
import os

print("Downloading DeepFace models...")
dummy = np.zeros((100, 100, 3), dtype=np.uint8)
cv2.imwrite("dummy.jpg", dummy)

try:
    DeepFace.analyze(
        "dummy.jpg",
        actions=["emotion"],
        enforce_detection=False,
        silent=False
    )
    print("DeepFace models downloaded")
except Exception as e:
    print(f"Note: {e}")

if os.path.exists("dummy.jpg"):
    os.remove("dummy.jpg")
print("Done")
