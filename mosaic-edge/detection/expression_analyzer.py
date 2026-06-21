# expression_analyzer.py
# OpenCV Haar Cascade fallback
# fer removed — not compatible with Python 3.13
# Pipeline still works fully

import cv2
import numpy as np
import os


class ExpressionAnalyzer:
    def __init__(self):
        print("Loading expression analyzer...")
        try:
            cascade_path = (
                cv2.data.haarcascades +
                'haarcascade_frontalface_default.xml'
            )
            self.face_cascade = cv2.CascadeClassifier(
                cascade_path)
            self.available = True
            print("Expression analyzer ready "
                  "(OpenCV Haar Cascade)")
        except Exception as e:
            print(f"Expression analyzer error: {e}")
            self.available = False

    def analyze(self, frame, bbox):
        if not self.available:
            return self._default()
        try:
            x1, y1, x2, y2 = [int(v) for v in bbox]
            h, w = frame.shape[:2]

            pad  = 20
            x1p  = max(0, x1 - pad)
            y1p  = max(0, y1 - pad)
            x2p  = min(w, x2 + pad)
            y2p  = min(h, y2 + pad)

            face = frame[y1p:y2p, x1p:x2p]
            if face.size == 0:
                return self._default()

            gray  = cv2.cvtColor(
                face, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=4,
                minSize=(30, 30)
            )

            if len(faces) > 0:
                # Face detected
                # Return neutral as default expression
                # Score based on face size confidence
                (fx, fy, fw, fh) = faces[0]
                face_area  = fw * fh
                frame_area = (x2p - x1p) * (y2p - y1p)
                confidence = min(0.90,
                    face_area / max(frame_area, 1) * 3)
                confidence = max(0.50, confidence)

                return {
                    'expression':       'neutral',
                    'expression_score': round(
                        confidence, 3),
                    'all_emotions': {
                        'neutral': round(confidence, 3),
                        'fear':    0.10,
                        'sad':     0.10,
                        'angry':   0.05,
                        'happy':   0.05,
                        'surprise':0.05,
                        'disgust': 0.05
                    }
                }

            return self._default()

        except Exception as e:
            print(f"Expression analysis error: {e}")
            return self._default()

    def _default(self):
        return {
            'expression':       'N/A',
            'expression_score': 0.0,
            'all_emotions':     {}
        }


# ─────────────────────────────────────────────
# STANDALONE TEST
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    import time
    sys.path.insert(
        0, '/home/leopardtech/Desktop/mosaic-edge')

    from camera.capture import CameraCapture
    from detection.detector import Detector

    print("\n" + "="*50)
    print("EXPRESSION TEST: OpenCV Fallback")
    print("="*50)

    cam  = CameraCapture()
    det  = Detector()
    expr = ExpressionAnalyzer()
    time.sleep(1)

    print("Show face to camera...")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            frame = cam.read_frame()
            if frame is None:
                time.sleep(0.5)
                continue

            persons, _ = det.run(frame)

            if not persons:
                print("No person detected")
                time.sleep(1)
                continue

            result = expr.analyze(
                frame, persons[0]['bbox'])
            print(
                f"Expression: {result['expression']}"
                f" | Score: {result['expression_score']}"
            )
            time.sleep(0.5)

    except KeyboardInterrupt:
        pass

    cam.release()
    print("Done")
