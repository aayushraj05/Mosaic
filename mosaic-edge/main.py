# main.py
# MOSAIC Edge Intelligence
# Full pipeline with real-time output

import env_setup  # must be first import
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'
os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
os.environ['YOLO_VERBOSE'] = 'False'
from utils.telemetry_logger import (
    log_telemetry,
    log_detection,
    log_heartbeat
)
import sys
import time
import logging
import threading
import cv2
from datetime import datetime

# Suppress model logs
os.environ['YOLO_VERBOSE'] = 'False'
logging.getLogger('ultralytics').setLevel(
    logging.WARNING)

import config
from camera.capture import CameraCapture
from detection.detector import Detector
from detection.pose_analyzer import PoseAnalyzer
from detection.expression_analyzer import ExpressionAnalyzer
from detection.confidence import ConfidenceAssembler
from actuation.motor_controller import MotorController
from utils.image_utils import (
    draw_person_box,
    draw_object_box,
    draw_legend,
    encode_frame
)
from comms.mqtt_client import MQTTClient

# Check if display available
DISPLAY_AVAILABLE = os.environ.get('DISPLAY') is not None

# ─────────────────────────────────────────────
# Policy update from cloud
# ─────────────────────────────────────────────
def on_policy_received(payload):
    try:
        new_threshold = payload.get('threshold')
        if new_threshold:
            config.THRESHOLD = float(
                new_threshold)
            print(f"Threshold updated: "
                  f"{config.THRESHOLD}")
            motor.rescan_pulse()  # ← add this
    except Exception as e:
        print(f"Policy error: {e}")

# ─────────────────────────────────────────────
# Initialize
# ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("  MOSAIC Edge Node Starting")
print(f"  Device ID:  {config.DEVICE_ID}")
print(f"  Threshold:  {config.THRESHOLD}")
print(f"  Floor:      {config.FLOOR}")
print("=" * 55 + "\n")

os.makedirs('data', exist_ok=True)

camera     = CameraCapture()
detector   = Detector()
pose       = PoseAnalyzer()
expression = ExpressionAnalyzer()
confidence = ConfidenceAssembler()
motor      = MotorController()

mqtt = MQTTClient(on_policy_received)
mqtt.connect()
time.sleep(3)

# ─────────────────────────────────────────────
# Heartbeat thread
# ─────────────────────────────────────────────
def heartbeat_loop():
    while True:
        time.sleep(config.HEARTBEAT_INTERVAL)

        ts = datetime.utcnow().isoformat()

        heartbeat = {
            'device_id':   config.DEVICE_ID,
            'drone_id':    config.DEVICE_ID,
            'timestamp':   ts,
            'status':      'scanning',
            'simulated':   False,
            'flight': {
                'mode':       'ACTIVE',
                'altitude_m': config.ALTITUDE,
                'speed_ms':   config.FLIGHT_SPEED,
                'heading_deg': 0.0
            },
            'location': {
                'lat': config.GPS_LAT,
                'lon': config.GPS_LON,
                'gps_fix': True
            },
            'power': {
                'battery_pct':    config.BATTERY,
                'battery_health': 'GOOD'
            },
            'comms': {
                'signal_dbm':      config.SIGNAL_STRENGTH,
                'packet_loss_pct': 0.0
            },
            'sensors': {
                'temperature_c':  config.TEMPERATURE,
                'cpu_usage_pct':  0.0,
                'ram_used_mb':    0.0
            },
            'mission_stats': {
                'detections_today':  0,
                'confirmed_victims': 0
            },
            'detection': None
        }

        log_heartbeat(heartbeat)
        log_telemetry(heartbeat)
        print(f"[HEARTBEAT] {ts} : scanning")
        mqtt.publish_detection(heartbeat)

heartbeat_thread = threading.Thread(
    target=heartbeat_loop, daemon=True)
heartbeat_thread.start()

# ─────────────────────────────────────────────
# Save frame to data folder
# ─────────────────────────────────────────────
def save_frame(frame, prefix):
    ts       = datetime.now().strftime('%H%M%S')
    filename = f"data/{prefix}_{ts}.jpg"
    cv2.imwrite(filename, frame)
    return filename

# ─────────────────────────────────────────────
# Print detection summary
# ─────────────────────────────────────────────
def print_detection(idx, person,
                    pose_r, expr_r, score_r,
                    saved_path=None):
    print(f"\n  --- PERSON {idx+1} ---")
    print(f"  YOLO Score:   {person['confidence']}")
    print(f"  Pose Score:   {pose_r['pose_score']}")
    print(f"  Expression:   {expr_r['expression']}"
          f" ({expr_r['expression_score']})")
    print(f"  Final Score:  {score_r['final_score']}")
    print(f"  Status:       "
          f"{score_r['status'].upper()}")
    print(f"  Priority:     {score_r['priority']}")
    print(f"  Indicators:   "
          f"{pose_r['indicators']}")

    if score_r['status'] == 'confirmed':
        print(f"  Action:       MOTORS SPINNING")
        print(f"  Alert:        VICTIM CONFIRMED")
        if saved_path:
            print(f"  Saved:        {saved_path}")

    elif score_r['status'] == 'uncertain':
        print(f"  Action:       ESCALATING TO CLOUD")
        print(f"  Alert:        OPERATOR REVIEW NEEDED")
        if saved_path:
            print(f"  Saved:        {saved_path}")

    elif score_r['status'] == 'possible_missed_victim':
        print(f"  Action:       LOW CONFIDENCE LOG")
        print(f"  Alert:        POSSIBLE MISSED VICTIM")

# ─────────────────────────────────────────────
# Main detection loop
# ─────────────────────────────────────────────
print("Detection loop starting...")
if DISPLAY_AVAILABLE:
    print("Camera window will open")
else:
    print("Headless mode — saving frames to data/")
print("Press Ctrl+C to stop\n")

frame_count = 0

try:
    while True:
        frame = camera.read_frame()
        if frame is None:
            time.sleep(0.1)
            continue

        frame_count += 1
        output = frame.copy()

        # Run YOLO
        persons, objects = detector.run(frame)

        # Draw object boxes
        for obj in objects:
            output = draw_object_box(output, obj)

        # Print frame header only when detections change
        if persons:
            ts = datetime.now().strftime('%H:%M:%S')
            print(f"\n{'='*55}")
            print(f"MOSAIC -- Frame {frame_count}"
                  f" | {ts}")
            print(f"Persons: {len(persons)}"
                  f" | Objects: {len(objects)}")
            print(f"{'='*55}")

        # Process each person
        for idx, person in enumerate(persons):

            # Pose analysis
            pose_r = pose.analyze(
                frame, person['bbox'])

            # Expression analysis
            expr_r = expression.analyze(
                frame, person['bbox'])

            # Confidence score
            score_r = confidence.compute(
                person['confidence'],
                pose_r['pose_score'],
                expr_r['expression'],
                expr_r['expression_score']
            )

            # Draw on frame
            output = draw_person_box(
                output, idx, person,
                pose_r, expr_r, score_r)

            saved_path = None

            # Handle each state
            if score_r['status'] == 'confirmed':
                # Save annotated frame
                saved_path = save_frame(output, 'confirmed')
                priority = score_r.get('priority', 'LOW')
                if priority == 'CRITICAL': motor.alert_pulse()
                else: motor.confirmation_spin()
                # Build and publish payload
                payload = {
					'device_id':   config.DEVICE_ID,
					'drone_id':    config.DEVICE_ID,
					'timestamp':   datetime.utcnow().isoformat(),
					'simulated':   False,
					'flight': {
						'mode':        'ACTIVE',
						'altitude_m':  config.ALTITUDE,
						'speed_ms':    config.FLIGHT_SPEED,
						'heading_deg': 0.0
					},
					'location': {
						'lat':     config.GPS_LAT,
						'lon':     config.GPS_LON,
						'gps_fix': True
					},
					'power': {
						'battery_pct':    config.BATTERY,
						'battery_health': 'GOOD'
					},
					'comms': {
						'signal_dbm':      config.SIGNAL_STRENGTH,
						'packet_loss_pct': 0.0
					},
					'sensors': {
						'temperature_c': config.TEMPERATURE,
						'cpu_usage_pct': 0.0,
						'ram_used_mb':   0.0
					},
					'mission_stats': {
						'detections_today':  0,
						'confirmed_victims': 0
					},
					'detection': {
						'status':           'confirmed',
						'confidence':       score_r['final_score'],
						'priority':         score_r['priority'],
						'victim_confirmed': True,
						'yolo_score':       person['confidence'],
						'pose_score':       pose_r['pose_score'],
						'expression':       expr_r['expression'],
						'expression_score': expr_r['expression_score'],
						'pose_indicators':  pose_r['indicators'],
						'indicators':       pose_r['indicators'],
						'requires_review':  False,
						'threshold_used':   config.THRESHOLD,
						'floor_used':       config.FLOOR
					}
				}
                log_telemetry(payload)
                log_detection(payload)
                # Add before each mqtt.publish_detection(payload):
                print(f"Publishing payload keys: {list(payload.keys())}")
                if 'detection' in payload: print(f"Detection keys: {list(payload['detection'].keys())}")
                mqtt.publish_detection(payload)

            elif score_r['status'] == 'uncertain':
                # Save annotated frame with scores
                saved_path = save_frame(
                    output, 'uncertain')
                # Encode image for cloud
                img_b64 = encode_frame(frame)
                payload = {
					'device_id':   config.DEVICE_ID,
					'drone_id':    config.DEVICE_ID,
					'timestamp':   datetime.utcnow().isoformat(),
					'simulated':   False,
					'flight': {
						'mode':        'ACTIVE',
						'altitude_m':  config.ALTITUDE,
						'speed_ms':    config.FLIGHT_SPEED,
						'heading_deg': 0.0
					},
					'location': {
						'lat':     config.GPS_LAT,
						'lon':     config.GPS_LON,
						'gps_fix': True
					},
					'power': {
						'battery_pct':    config.BATTERY,
						'battery_health': 'GOOD'
					},
					'comms': {
						'signal_dbm':      config.SIGNAL_STRENGTH,
						'packet_loss_pct': 0.0
					},
					'sensors': {
						'temperature_c': config.TEMPERATURE,
						'cpu_usage_pct': 0.0,
						'ram_used_mb':   0.0
					},
					'mission_stats': {
						'detections_today':  0,
						'confirmed_victims': 0
					},
					'detection': {
						'status':           'uncertain',
						'confidence':       score_r['final_score'],
						'priority':         score_r['priority'],
						'victim_confirmed': False,
						'yolo_score':       person['confidence'],
						'pose_score':       pose_r['pose_score'],
						'expression':       expr_r['expression'],
						'expression_score': expr_r['expression_score'],
						'pose_indicators':  pose_r['indicators'],
						'indicators':       pose_r['indicators'],
						'requires_review':  True,
						'threshold_used':   config.THRESHOLD,
						'floor_used':       config.FLOOR,
						'image_b64':        encode_frame(frame)
					}
				}
                log_telemetry(payload)
                log_detection(payload)
                # Add before each mqtt.publish_detection(payload):
                print(f"Publishing payload keys: {list(payload.keys())}")
                if 'detection' in payload: print(f"Detection keys: {list(payload['detection'].keys())}")
                mqtt.publish_detection(payload)

            elif score_r['status'] == \
                    'possible_missed_victim':
                saved_path = save_frame(
                    output, 'missed')
                payload = {
					'device_id':   config.DEVICE_ID,
					'drone_id':    config.DEVICE_ID,
					'timestamp':   datetime.utcnow().isoformat(),
					'simulated':   False,
					'flight': {
						'mode':        'ACTIVE',
						'altitude_m':  config.ALTITUDE,
						'speed_ms':    config.FLIGHT_SPEED,
						'heading_deg': 0.0
					},
					'location': {
						'lat':     config.GPS_LAT,
						'lon':     config.GPS_LON,
						'gps_fix': True
					},
					'power': {
						'battery_pct':    config.BATTERY,
						'battery_health': 'GOOD'
					},
					'comms': {
						'signal_dbm':      config.SIGNAL_STRENGTH,
						'packet_loss_pct': 0.0
					},
					'sensors': {
						'temperature_c': config.TEMPERATURE,
						'cpu_usage_pct': 0.0,
						'ram_used_mb':   0.0
					},
					'mission_stats': {
						'detections_today':  0,
						'confirmed_victims': 0
					},
					'detection': {
						'status':           'possible_missed_victim',
						'confidence':       score_r['final_score'],
						'priority':         'LOW',
						'victim_confirmed': False,
						'yolo_score':       person['confidence'],
						'pose_score':       pose_r['pose_score'],
						'expression':       expr_r['expression'],
						'expression_score': expr_r['expression_score'],
						'pose_indicators':  pose_r['indicators'],
						'indicators':       pose_r['indicators'],
						'requires_review':  False,
						'threshold_used':   config.THRESHOLD,
						'floor_used':       config.FLOOR
					}
				}
                log_telemetry(payload)
                # Add before each mqtt.publish_detection(payload):
                print(f"Publishing payload keys: {list(payload.keys())}")
                if 'detection' in payload: print(f"Detection keys: {list(payload['detection'].keys())}")
                mqtt.publish_detection(payload)

            # Print to terminal
            print_detection(
                idx, person,
                pose_r, expr_r, score_r,
                saved_path)

        # Draw pose skeleton
        if persons:
            output = pose.draw_keypoints(output)

        # Draw legend
        output = draw_legend(output)

        # Show or save frame
        if DISPLAY_AVAILABLE:
            cv2.imshow("MOSAIC Edge", output)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\nQuit requested")
                break
        else:
            # Headless — save every 30 frames
            if frame_count % 30 == 0:
                save_frame(output, 'scan')

        # Log objects
        if objects and frame_count % 50 == 0:
            print(f"\nEnvironment: "
                  f"{[o['class'] for o in objects]}")

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\n\nShutting down MOSAIC...")

finally:
    camera.release()
    motor.cleanup()
    if DISPLAY_AVAILABLE:
        cv2.destroyAllWindows()
    mqtt.disconnect()
    print("MOSAIC shutdown complete")
    print(f"Frames processed: {frame_count}")
    print(f"Check data/ folder for saved images")
