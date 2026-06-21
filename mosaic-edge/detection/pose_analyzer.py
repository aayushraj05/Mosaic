# detection/pose_analyzer.py
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
logging.getLogger('ultralytics').setLevel(
    logging.WARNING)
sys.path.append(
    os.path.dirname(os.path.dirname(__file__)))

from ultralytics import YOLO
import config


class PoseAnalyzer:
    def __init__(self):
        model_path = os.path.join(
            config.MODELS_DIR, 'yolov8n-pose.pt')
        print("Loading Pose model...")
        self.model = YOLO(model_path)
        print("Pose analyzer ready")

        self.NOSE           = 0
        self.LEFT_EYE       = 1
        self.RIGHT_EYE      = 2
        self.LEFT_EAR       = 3
        self.RIGHT_EAR      = 4
        self.LEFT_SHOULDER  = 5
        self.RIGHT_SHOULDER = 6
        self.LEFT_ELBOW     = 7
        self.RIGHT_ELBOW    = 8
        self.LEFT_WRIST     = 9
        self.RIGHT_WRIST    = 10
        self.LEFT_HIP       = 11
        self.RIGHT_HIP      = 12
        self.LEFT_KNEE      = 13
        self.RIGHT_KNEE     = 14
        self.LEFT_ANKLE     = 15
        self.RIGHT_ANKLE    = 16

        # Cache last keypoints for drawing
        self._last_keypoints = []

    def analyze(self, frame, bbox=None):
        try:
            results = self.model(
                frame, verbose=False)
            self._last_keypoints = []

            if not results:
                return self._default()

            for result in results:
                if result.keypoints is None:
                    continue
                kps = result.keypoints.data
                if kps is None or len(kps) == 0:
                    continue

                # Cache ALL persons keypoints for drawing
                for kp in kps:
                    self._last_keypoints.append(
                        kp.cpu().numpy())

                # Analyze first person
                keypoints = kps[0].cpu().numpy()
                return self._analyze_keypoints(keypoints)

            return self._default()

        except Exception as e:
            print(f"Pose error: {e}")
            return self._default()

    def _default(self):
        return {
            'pose_score': 0.30,
            'indicators': ['pose_not_visible'],
            'keypoints':  None
        }

    def _analyze_keypoints(self, kp):
        indicators = []
        pose_score = 0.50

        def get_kp(idx):
            if idx < len(kp):
                return (float(kp[idx][0]),
                        float(kp[idx][1]),
                        float(kp[idx][2]))
            return 0.0, 0.0, 0.0

        nose_x,  nose_y,  nose_conf  = get_kp(self.NOSE)
        ls_x,    ls_y,    ls_conf    = get_kp(self.LEFT_SHOULDER)
        rs_x,    rs_y,    rs_conf    = get_kp(self.RIGHT_SHOULDER)
        lw_x,    lw_y,    lw_conf    = get_kp(self.LEFT_WRIST)
        rw_x,    rw_y,    rw_conf    = get_kp(self.RIGHT_WRIST)
        lh_x,    lh_y,    lh_conf    = get_kp(self.LEFT_HIP)
        rh_x,    rh_y,    rh_conf    = get_kp(self.RIGHT_HIP)
        lk_x,    lk_y,    lk_conf    = get_kp(self.LEFT_KNEE)
        rk_x,    rk_y,    rk_conf    = get_kp(self.RIGHT_KNEE)

        # CHECK 1 — Fallen or Upright
        if nose_conf > 0.3 and (
                lh_conf > 0.3 or rh_conf > 0.3):
            avg_hip_y = 0.0
            count = 0
            if lh_conf > 0.3:
                avg_hip_y += lh_y
                count += 1
            if rh_conf > 0.3:
                avg_hip_y += rh_y
                count += 1
            avg_hip_y /= count

            if abs(nose_y - avg_hip_y) < 60:
                indicators.append('fallen')
                pose_score = 0.85
            else:
                indicators.append('upright')
        else:
            indicators.append('upright')

        # CHECK 2 — Arms Raised
        left_raised = (lw_conf > 0.3 and
                       ls_conf > 0.3 and
                       lw_y < ls_y)
        right_raised = (rw_conf > 0.3 and
                        rs_conf > 0.3 and
                        rw_y < rs_y)

        if left_raised and right_raised:
            indicators.append('both_arms_raised')
            pose_score = max(pose_score, 0.90)
        elif left_raised or right_raised:
            indicators.append('arms_raised')
            pose_score = max(pose_score, 0.80)

        # CHECK 3 — Waving
        if nose_conf > 0.3:
            if ((lw_conf > 0.3 and lw_y < nose_y) or
                    (rw_conf > 0.3 and rw_y < nose_y)):
                indicators.append('waving')
                pose_score = max(pose_score, 0.85)

        # CHECK 4 — Possibly Unconscious
        if ('fallen' in indicators and
                'arms_raised' not in indicators and
                'both_arms_raised' not in indicators and
                lw_conf < 0.4 and rw_conf < 0.4):
            indicators.append('possibly_unconscious')
            pose_score = max(pose_score, 0.88)

        # CHECK 5 — Crouching
        if (lh_conf > 0.3 and lk_conf > 0.3 and
                'fallen' not in indicators):
            if abs(lh_y - lk_y) < 40:
                indicators.append('crouching')
                pose_score = max(pose_score, 0.60)

        # CHECK 6 — Active Distress
        if ('fallen' in indicators and
                ('arms_raised' in indicators or
                 'both_arms_raised' in indicators)):
            indicators.append('active_distress')
            pose_score = max(pose_score, 0.95)

        if not indicators:
            indicators.append('pose_detected')

        return {
            'pose_score': round(pose_score, 3),
            'indicators': indicators,
            'keypoints':  kp
        }

    def draw_keypoints(self, frame):
        # Uses cached keypoints from last analyze()
        # Does NOT run model again — saves compute
        import cv2
        connections = [
            (self.NOSE,           self.LEFT_EYE),
            (self.NOSE,           self.RIGHT_EYE),
            (self.LEFT_EYE,       self.LEFT_EAR),
            (self.RIGHT_EYE,      self.RIGHT_EAR),
            (self.LEFT_SHOULDER,  self.RIGHT_SHOULDER),
            (self.LEFT_SHOULDER,  self.LEFT_ELBOW),
            (self.LEFT_ELBOW,     self.LEFT_WRIST),
            (self.RIGHT_SHOULDER, self.RIGHT_ELBOW),
            (self.RIGHT_ELBOW,    self.RIGHT_WRIST),
            (self.LEFT_SHOULDER,  self.LEFT_HIP),
            (self.RIGHT_SHOULDER, self.RIGHT_HIP),
            (self.LEFT_HIP,       self.RIGHT_HIP),
            (self.LEFT_HIP,       self.LEFT_KNEE),
            (self.LEFT_KNEE,      self.LEFT_ANKLE),
            (self.RIGHT_HIP,      self.RIGHT_KNEE),
            (self.RIGHT_KNEE,     self.RIGHT_ANKLE),
        ]

        for keypoints in self._last_keypoints:
            for s, e in connections:
                if (s < len(keypoints) and
                        e < len(keypoints)):
                    x1, y1, c1 = keypoints[s]
                    x2, y2, c2 = keypoints[e]
                    if c1 > 0.3 and c2 > 0.3:
                        cv2.line(
                            frame,
                            (int(x1), int(y1)),
                            (int(x2), int(y2)),
                            (255, 0, 255), 2)
            for kp in keypoints:
                x, y, conf = int(kp[0]), int(kp[1]), kp[2]
                if conf > 0.3:
                    cv2.circle(
                        frame, (x, y), 5,
                        (0, 255, 255), -1)

        return frame


# ─────────────────────────────────────────────
# STANDALONE TEST
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import cv2
    import time
    import sys
    sys.path.insert(0, '/home/pi/mosaic-edge')

    from camera.capture import CameraCapture

    print("Testing pose analyzer alone...")
    cam  = CameraCapture()
    pose = PoseAnalyzer()
    time.sleep(1)

    print("Stand in front of camera...")
    print("Raise arms to test arms_raised")
    print("Lie down to test fallen")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            frame = cam.read_frame()
            if frame is None:
                continue

            result = pose.analyze(frame)
            print(f"Pose Score: {result['pose_score']}"
                  f" | Indicators: "
                  f"{result['indicators']}")
            time.sleep(0.5)

    except KeyboardInterrupt:
        pass

    cam.release()
    print("Pose test complete")
