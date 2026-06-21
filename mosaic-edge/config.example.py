# config.example.py
# ─────────────────────────────────────────────
# MOSAIC Edge Configuration Template
# Copy this file to config.py
# Fill in your actual values
# NEVER commit config.py to GitHub
# ─────────────────────────────────────────────
# cp config.example.py config.py
# nano config.py
# ─────────────────────────────────────────────

import json
import os

# ─────────────────────────────────────────────
# DEVICE IDENTITY
# ─────────────────────────────────────────────
DEVICE_ID    = "mosaic-node-01"
DEVICE_TYPE  = "quadcopter"
MISSION      = "flood_search_rescue"

# ─────────────────────────────────────────────
# AWS IOT CORE
# Get endpoint from:
# AWS Console -> IoT Core -> Settings
# -> Device data endpoint
# ─────────────────────────────────────────────
IOT_ENDPOINT = "YOUR_ENDPOINT_HERE.iot.ap-south-1.amazonaws.com"

CERTS_DIR    = os.path.join(
    os.path.dirname(__file__), 'certs')

# ─────────────────────────────────────────────
# DETECTION THRESHOLDS
# THRESHOLD: score above this = CONFIRMED
# FLOOR: score above this = UNCERTAIN
# Below FLOOR = MISSED or SCANNING
# ─────────────────────────────────────────────
THRESHOLD = 0.60
FLOOR     = 0.30

# ─────────────────────────────────────────────
# MODEL PATHS
# Download models using download_models.py
# ─────────────────────────────────────────────
MODELS_DIR      = os.path.join(
    os.path.dirname(__file__), 'models')
YOLO_MODEL      = 'yolov8n.pt'
YOLO_POSE_MODEL = 'yolov8n-pose.pt'

# ─────────────────────────────────────────────
# FLIGHT TELEMETRY DEFAULTS
# Update GPS coordinates to your location
# ─────────────────────────────────────────────
ALTITUDE           = 50.0
FLIGHT_SPEED       = 5.0
GPS_LAT            = 0.0000
GPS_LON            = 0.0000
BATTERY            = 100.0
TEMPERATURE        = 45.0
SIGNAL_STRENGTH    = -60
HEARTBEAT_INTERVAL = 60

# ─────────────────────────────────────────────
# MOTOR AND ESC SETTINGS
# Avionics C2826 1000KV on F450 frame
# GPIO pin numbers for ESC signal wires
# ─────────────────────────────────────────────
MOTOR_TYPE     = 'brushless_esc'
MOTOR_GPIO_FL  = 17
MOTOR_GPIO_FR  = 18
MOTOR_GPIO_RL  = 27
MOTOR_GPIO_RR  = 22
ESC_MIN_US     = 1000
ESC_ARM_US     = 1050
ESC_IDLE_US    = 1150
ESC_PWM_FREQ   = 50
BENCH_SAFE_MAX = 1250

# ─────────────────────────────────────────────
# ADAPTIVE RULES FILE
# Stores learned threshold between sessions
# ─────────────────────────────────────────────
RULES_FILE = os.path.join(
    os.path.dirname(__file__),
    'adaptive_rules.json')


def load_rules():
    global THRESHOLD, FLOOR
    try:
        if os.path.exists(RULES_FILE):
            with open(RULES_FILE, 'r') as f:
                rules = json.load(f)
                THRESHOLD = float(rules.get(
                    'threshold', THRESHOLD))
                FLOOR     = float(rules.get(
                    'floor', FLOOR))
            print(f"Rules loaded: "
                  f"threshold={THRESHOLD} "
                  f"floor={FLOOR}")
    except Exception as e:
        print(f"Rules load error: {e}")


load_rules()