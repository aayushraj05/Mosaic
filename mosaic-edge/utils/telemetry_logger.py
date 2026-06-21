# utils/telemetry_logger.py
# Saves all telemetry data to CSV files
# Runs alongside MQTT publish
# Data saved even if cloud is offline

import csv
import os
from datetime import datetime


DATA_DIR = os.path.join(
    os.path.dirname(
    os.path.dirname(__file__)), 'data')


def ensure_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def get_path(filename):
    return os.path.join(DATA_DIR, filename)


# ─────────────────────────────────────────────
# TELEMETRY CSV (every frame with detection)
# ─────────────────────────────────────────────
TELEMETRY_HEADERS = [
    'timestamp',
    'device_id',
    'simulated',

    # Flight
    'flight_mode',
    'altitude_m',
    'speed_ms',
    'heading_deg',

    # Location
    'lat',
    'lon',
    'gps_fix',

    # Power
    'battery_pct',
    'battery_health',
    'voltage_v',

    # Comms
    'signal_dbm',
    'packet_loss_pct',

    # Sensors
    'temperature_c',
    'cpu_usage_pct',
    'ram_used_mb',
    'camera_fps',

    # Environment
    'visibility',
    'wind_speed_ms',
    'rain_detected',

    # Mission
    'detections_today',
    'confirmed_victims',

    # Detection result
    'detection_status',
    'detection_confidence',
    'detection_priority',
    'yolo_score',
    'pose_score',
    'expression',
    'expression_score',
    'pose_indicators',
    'victim_confirmed',
    'requires_review',
    'threshold_used'
]


def log_telemetry(payload):
    ensure_dir()
    device_id = (payload.get('device_id') or
                 payload.get('drone_id') or
                 'unknown')
    filename  = get_path(
        f"telemetry_{device_id}.csv")
    file_exists = os.path.exists(filename)

    detection = payload.get('detection') or {}
    flight    = payload.get('flight', {})
    location  = payload.get('location', {})
    power     = payload.get('power', {})
    comms     = payload.get('comms', {})
    sensors   = payload.get('sensors', {})
    env       = payload.get('environment', {})
    mission   = payload.get('mission_stats', {})

    row = {
        'timestamp':           payload.get(
                               'timestamp',
                               datetime.utcnow(
                               ).isoformat()),
        'device_id':           device_id,
        'simulated':           payload.get(
                               'simulated', False),

        'flight_mode':         flight.get(
                               'mode', 'ACTIVE'),
        'altitude_m':          flight.get(
                               'altitude_m', 0),
        'speed_ms':            flight.get(
                               'speed_ms', 0),
        'heading_deg':         flight.get(
                               'heading_deg', 0),

        'lat':                 location.get(
                               'lat', 0),
        'lon':                 location.get(
                               'lon', 0),
        'gps_fix':             location.get(
                               'gps_fix', False),

        'battery_pct':         power.get(
                               'battery_pct', 0),
        'battery_health':      power.get(
                               'battery_health', ''),
        'voltage_v':           power.get(
                               'voltage_v', 0),

        'signal_dbm':          comms.get(
                               'signal_dbm', 0),
        'packet_loss_pct':     comms.get(
                               'packet_loss_pct', 0),

        'temperature_c':       sensors.get(
                               'temperature_c', 0),
        'cpu_usage_pct':       sensors.get(
                               'cpu_usage_pct', 0),
        'ram_used_mb':         sensors.get(
                               'ram_used_mb', 0),
        'camera_fps':          sensors.get(
                               'camera_fps', 0),

        'visibility':          env.get(
                               'visibility', ''),
        'wind_speed_ms':       env.get(
                               'wind_speed_ms', 0),
        'rain_detected':       env.get(
                               'rain_detected',
                               False),

        'detections_today':    mission.get(
                               'detections_today',
                               0),
        'confirmed_victims':   mission.get(
                               'confirmed_victims',
                               0),

        'detection_status':    detection.get(
                               'status', 'scanning'),
        'detection_confidence':detection.get(
                               'confidence', 0),
        'detection_priority':  detection.get(
                               'priority', ''),
        'yolo_score':          detection.get(
                               'yolo_score', 0),
        'pose_score':          detection.get(
                               'pose_score', 0),
        'expression':          detection.get(
                               'expression', ''),
        'expression_score':    detection.get(
                               'expression_score',
                               0),
        'pose_indicators':     str(detection.get(
                               'pose_indicators',
                               detection.get(
                               'indicators', []))),
        'victim_confirmed':    detection.get(
                               'victim_confirmed',
                               False),
        'requires_review':     detection.get(
                               'requires_review',
                               False),
        'threshold_used':      detection.get(
                               'threshold_used',
                               0.60)
    }

    try:
        with open(filename, 'a',
                  newline='') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=TELEMETRY_HEADERS)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
    except Exception as e:
        print(f"CSV telemetry error: {e}")


# ─────────────────────────────────────────────
# DETECTIONS ONLY CSV
# (only rows where person detected)
# ─────────────────────────────────────────────
DETECTION_HEADERS = [
    'timestamp',
    'device_id',
    'status',
    'priority',
    'confidence',
    'yolo_score',
    'pose_score',
    'expression',
    'expression_score',
    'pose_indicators',
    'victim_confirmed',
    'requires_review',
    'threshold_used',
    'lat',
    'lon',
    'altitude_m',
    'battery_pct'
]


def log_detection(payload):
    detection = payload.get('detection')
    if not detection:
        return

    ensure_dir()
    device_id  = (payload.get('device_id') or
                  payload.get('drone_id') or
                  'unknown')
    filename   = get_path(
        f"detections_{device_id}.csv")
    file_exists= os.path.exists(filename)

    location = payload.get('location', {})
    flight   = payload.get('flight', {})
    power    = payload.get('power', {})

    row = {
        'timestamp':       payload.get(
                           'timestamp',
                           datetime.utcnow(
                           ).isoformat()),
        'device_id':       device_id,
        'status':          detection.get(
                           'status', ''),
        'priority':        detection.get(
                           'priority', ''),
        'confidence':      detection.get(
                           'confidence', 0),
        'yolo_score':      detection.get(
                           'yolo_score', 0),
        'pose_score':      detection.get(
                           'pose_score', 0),
        'expression':      detection.get(
                           'expression', ''),
        'expression_score':detection.get(
                           'expression_score',
                           0),
        'pose_indicators': str(detection.get(
                           'pose_indicators',
                           detection.get(
                           'indicators', []))),
        'victim_confirmed':detection.get(
                           'victim_confirmed',
                           False),
        'requires_review': detection.get(
                           'requires_review',
                           False),
        'threshold_used':  detection.get(
                           'threshold_used',
                           0.60),
        'lat':             location.get('lat', 0),
        'lon':             location.get('lon', 0),
        'altitude_m':      flight.get(
                           'altitude_m', 0),
        'battery_pct':     power.get(
                           'battery_pct', 0)
    }

    try:
        with open(filename, 'a',
                  newline='') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=DETECTION_HEADERS)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
    except Exception as e:
        print(f"CSV detection error: {e}")


# ─────────────────────────────────────────────
# HEARTBEAT CSV
# (one row per heartbeat/scan cycle)
# ─────────────────────────────────────────────
HEARTBEAT_HEADERS = [
    'timestamp',
    'device_id',
    'battery_pct',
    'battery_health',
    'altitude_m',
    'speed_ms',
    'lat',
    'lon',
    'temperature_c',
    'cpu_usage_pct',
    'signal_dbm',
    'detections_today',
    'confirmed_victims',
    'status'
]


def log_heartbeat(payload):
    ensure_dir()
    device_id  = (payload.get('device_id') or
                  payload.get('drone_id') or
                  'unknown')
    filename   = get_path(
        f"heartbeat_{device_id}.csv")
    file_exists= os.path.exists(filename)

    flight   = payload.get('flight', {})
    location = payload.get('location', {})
    power    = payload.get('power', {})
    sensors  = payload.get('sensors', {})
    comms    = payload.get('comms', {})
    mission  = payload.get('mission_stats', {})

    row = {
        'timestamp':         payload.get(
                             'timestamp',
                             datetime.utcnow(
                             ).isoformat()),
        'device_id':         device_id,
        'battery_pct':       power.get(
                             'battery_pct', 0),
        'battery_health':    power.get(
                             'battery_health', ''),
        'altitude_m':        flight.get(
                             'altitude_m', 0),
        'speed_ms':          flight.get(
                             'speed_ms', 0),
        'lat':               location.get(
                             'lat', 0),
        'lon':               location.get(
                             'lon', 0),
        'temperature_c':     sensors.get(
                             'temperature_c', 0),
        'cpu_usage_pct':     sensors.get(
                             'cpu_usage_pct', 0),
        'signal_dbm':        comms.get(
                             'signal_dbm', 0),
        'detections_today':  mission.get(
                             'detections_today',
                             0),
        'confirmed_victims': mission.get(
                             'confirmed_victims',
                             0),
        'status':            flight.get(
                             'mode', 'scanning')
    }

    try:
        with open(filename, 'a',
                  newline='') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=HEARTBEAT_HEADERS)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
    except Exception as e:
        print(f"CSV heartbeat error: {e}")