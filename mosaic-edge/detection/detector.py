# detection/detector.py
import env_setup  # must be first import
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'
os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
os.environ['YOLO_VERBOSE'] = 'False'
import sys
import logging

os.environ['YOLO_VERBOSE'] = 'False'
logging.getLogger('ultralytics').setLevel(logging.WARNING)

sys.path.append(
    os.path.dirname(os.path.dirname(__file__)))

from ultralytics import YOLO
import config


class Detector:
    def __init__(self):
        model_path = os.path.join(
            config.MODELS_DIR, 'yolov8n.pt')
        print(f"Loading YOLO detector...")
        self.model = YOLO(model_path)
        print("YOLO detector ready")

    def run(self, frame):
        results = self.model(
            frame, verbose=False)
        persons = []
        objects = []

        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                class_id   = int(box.cls[0])
                class_name = self.model.names[class_id]
                confidence = float(box.conf[0])
                bbox       = box.xyxy[0].tolist()

                entry = {
                    'class':      class_name,
                    'confidence': round(confidence, 3),
                    'bbox':       bbox
                }

                if class_name == 'person':
                    persons.append(entry)
                else:
                    objects.append(entry)

        return persons, objects


# ─────────────────────────────────────────────
# STANDALONE TEST
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import cv2
    import time
    import sys
    sys.path.insert(0, '/home/pi/mosaic-edge')

    from camera.capture import CameraCapture

    print("Testing detector alone...")
    cam = CameraCapture()
    det = Detector()
    time.sleep(1)

    print("Running detection on 5 frames...")
    for i in range(5):
        frame = cam.read_frame()
        if frame is None:
            print(f"Frame {i+1}: Camera failed")
            continue

        persons, objects = det.run(frame)

        print(f"\nFrame {i+1}:")
        print(f"  Persons: {len(persons)}")
        for p in persons:
            print(f"    → person confidence: "
                  f"{p['confidence']}")
        print(f"  Objects: "
              f"{[o['class'] for o in objects]}")
        time.sleep(0.5)

    cam.release()
    print("\nDetector test complete")
