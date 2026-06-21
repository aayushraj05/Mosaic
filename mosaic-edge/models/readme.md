# Models

YOLO model files are not included in this repository.
Model files are too large for GitHub (6MB to 14MB each)
and are downloaded directly from Ultralytics.

---

## Files Required in This Folder

| File | Size | Purpose |
|------|------|---------|
| yolov8n.pt | 6.2 MB | Person and object detection |
| yolov8n-pose.pt | 6.5 MB | Body pose keypoint analysis |

---

## How to Download Models

### Option 1 — Use Download Script (Recommended)
cd ~/Desktop/mosaic-edge
python3 download_models.py

### Option 2 — Download in Python Directly
cd ~/Desktop/mosaic-edge
python3 -c "
import os
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
from ultralytics import YOLO
import shutil
print('Downloading yolov8n.pt...')
YOLO('yolov8n.pt')
print('Downloading yolov8n-pose.pt...')
YOLO('yolov8n-pose.pt')
print('Moving to models folder...')
import glob
for f in glob.glob('*.pt'):
shutil.move(f, 'models/' + f)
print(f'Moved: {f}')
print('Done')
"

### Option 3 — Manual Download
Download from Ultralytics GitHub releases:
- yolov8n.pt: https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
- yolov8n-pose.pt: https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n-pose.pt

Place both files directly in this models/ folder.

---

## Verify Models Downloaded Correctly
ls -lh ~/Desktop/mosaic-edge/models/

Expected output:
-rw-r--r-- 1 leopardtech leopardtech 6.2M yolov8n.pt
-rw-r--r-- 1 leopardtech leopardtech 6.5M yolov8n-pose.pt

Test models load correctly:
cd ~/Desktop/mosaic-edge
python3 -c "
import sys, os
sys.path.insert(0, '.')
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
from detection.detector import Detector
from detection.pose_analyzer import PoseAnalyzer
det  = Detector()
pose = PoseAnalyzer()
print('Both models loaded successfully')
"

---

## Model Information

### YOLOv8n (Detection Model)
- Architecture: YOLOv8 nano
- Parameters: 3.2 million
- Size: 6.2 MB
- Speed on Pi 4: 10-15 FPS
- Accuracy: 85-90% person detection
- Trained on: COCO dataset 80 classes
- Classes used: person (class 0)

### YOLOv8n-Pose (Pose Model)
- Architecture: YOLOv8 nano pose
- Parameters: 3.3 million
- Size: 6.5 MB
- Speed on Pi 4: 8-12 FPS
- Keypoints: 17 body points per person
- Points: nose eyes ears shoulders
         elbows wrists hips knees ankles

---

## Why These Models

YOLOv8n chosen specifically because:
- Smallest YOLOv8 variant runs on ARM CPU
- No GPU required on Raspberry Pi 4
- Sufficient accuracy for disaster detection
- Real-time performance at 10-15 FPS
- Open source and free to use

For product version upgrade to:
- YOLOv8x with TensorRT on Jetson Orin
- 30+ FPS with 91-95% accuracy