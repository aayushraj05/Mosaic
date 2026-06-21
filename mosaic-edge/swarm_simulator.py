# swarm_simulator.py
# Run on LAPTOP
# Simulates 3 drone nodes publishing to IoT Core
# python3 swarm_simulator.py

import json
import time
import random
import math
import threading
import ssl
import sys
import os
sys.path.insert(
    0, '/home/leopardtech/Desktop/mosaic-edge')
import csv
from datetime import datetime
import paho.mqtt.client as mqtt
import env_setup
from utils.telemetry_logger import (
    log_telemetry,
    log_detection,
    log_heartbeat
)

# ─────────────────────────────────────────────
# CONFIG — UPDATE THESE
# ─────────────────────────────────────────────
IOT_ENDPOINT = "ahh2ps3fvnvou-ats.iot.ap-south-1.amazonaws.com"
CERTS_DIR    = "/home/leopardtech/Desktop/mosaic-edge/certs"
INTERVAL     = 5  # seconds between publishes

DATA_DIR = './data'
os.makedirs(DATA_DIR, exist_ok=True)

def log_to_csv(drone_id, payload):
    filename = os.path.join(
        DATA_DIR,
        f"telemetry_{drone_id}.csv")
    file_exists = os.path.exists(filename)

    detection = payload.get('detection') or {}
    flight    = payload.get('flight', {})
    location  = payload.get('location', {})
    power     = payload.get('power', {})
    sensors   = payload.get('sensors', {})
    mission   = payload.get('mission_stats', {})

    row = {
        'timestamp':       payload.get('timestamp'),
        'device_id':       drone_id,
        'altitude_m':      flight.get('altitude_m'),
        'speed_ms':        flight.get('speed_ms'),
        'battery_pct':     power.get('battery_pct'),
        'lat':             location.get('lat'),
        'lon':             location.get('lon'),
        'temperature_c':   sensors.get('temperature_c'),
        'cpu_pct':         sensors.get('cpu_usage_pct'),
        'detections_today':mission.get('detections_today'),
        'confirmed_victims':mission.get('confirmed_victims'),
        'detection_status':detection.get('status','scanning'),
        'confidence':      detection.get('confidence', 0),
        'priority':        detection.get('priority', ''),
        'expression':      detection.get('expression', ''),
        'indicators':      str(detection.get('pose_indicators', []))
    }

    headers = list(row.keys())
    with open(filename, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

# ─────────────────────────────────────────────
# ZONE STARTING POSITIONS
# ─────────────────────────────────────────────
DRONE_CONFIGS = {
    "mosaic-node-02": {
        "start_lat":      19.0800,
        "start_lon":      72.8800,
        "altitude":       48.0,
        "battery":        87.0,
        "speed":          4.5,
        "heading":        45.0,
        "patrol_radius":  0.002
    },
    "mosaic-node-03": {
        "start_lat":      19.0750,
        "start_lon":      72.8760,
        "altitude":       55.0,
        "battery":        92.0,
        "speed":          5.5,
        "heading":        135.0,
        "patrol_radius":  0.0025
    },
    "mosaic-node-04": {
        "start_lat":      19.0750,
        "start_lon":      72.8800,
        "altitude":       42.0,
        "battery":        78.0,
        "speed":          3.5,
        "heading":        270.0,
        "patrol_radius":  0.0015
    }
}

# ─────────────────────────────────────────────
# DETECTION SCENARIOS PER DRONE
# ─────────────────────────────────────────────
SCENARIOS = {
    "mosaic-node-02": [
        {
            "status":      "confirmed",
            "confidence":  0.91,
            "priority":    "CRITICAL",
            "expression":  "fear",
            "yolo_score":  0.94,
            "pose_score":  0.92,
            "expr_score":  0.85,
            "indicators":  ["fallen",
                           "possibly_unconscious"]
        },
        None, None,
        {
            "status":      "uncertain",
            "confidence":  0.54,
            "priority":    "MEDIUM",
            "expression":  "neutral",
            "yolo_score":  0.61,
            "pose_score":  0.55,
            "expr_score":  0.45,
            "indicators":  ["upright"]
        },
        None,
        {
            "status":      "confirmed",
            "confidence":  0.88,
            "priority":    "HIGH",
            "expression":  "sad",
            "yolo_score":  0.90,
            "pose_score":  0.88,
            "expr_score":  0.80,
            "indicators":  ["arms_raised", "waving"]
        },
        None, None,
        {
            "status":      "possible_missed_victim",
            "confidence":  0.22,
            "priority":    "LOW",
            "expression":  "N/A",
            "yolo_score":  0.25,
            "pose_score":  0.30,
            "expr_score":  0.0,
            "indicators":  ["pose_not_visible"]
        },
        None
    ],
    "mosaic-node-03": [
        None,
        {
            "status":      "confirmed",
            "confidence":  0.95,
            "priority":    "CRITICAL",
            "expression":  "fear",
            "yolo_score":  0.97,
            "pose_score":  0.96,
            "expr_score":  0.88,
            "indicators":  ["active_distress",
                           "both_arms_raised",
                           "fallen"]
        },
        None,
        {
            "status":      "uncertain",
            "confidence":  0.48,
            "priority":    "MEDIUM",
            "expression":  "neutral",
            "yolo_score":  0.52,
            "pose_score":  0.50,
            "expr_score":  0.40,
            "indicators":  ["crouching"]
        },
        None,
        {
            "status":      "confirmed",
            "confidence":  0.82,
            "priority":    "HIGH",
            "expression":  "sad",
            "yolo_score":  0.85,
            "pose_score":  0.83,
            "expr_score":  0.75,
            "indicators":  ["both_arms_raised",
                           "upright"]
        },
        None, None, None,
        {
            "status":      "confirmed",
            "confidence":  0.79,
            "priority":    "HIGH",
            "expression":  "fear",
            "yolo_score":  0.81,
            "pose_score":  0.80,
            "expr_score":  0.72,
            "indicators":  ["waving", "upright"]
        }
    ],
    "mosaic-node-04": [
        None, None,
        {
            "status":      "uncertain",
            "confidence":  0.55,
            "priority":    "MEDIUM",
            "expression":  "neutral",
            "yolo_score":  0.58,
            "pose_score":  0.56,
            "expr_score":  0.48,
            "indicators":  ["upright"]
        },
        None, None,
        {
            "status":      "confirmed",
            "confidence":  0.86,
            "priority":    "HIGH",
            "expression":  "fear",
            "yolo_score":  0.88,
            "pose_score":  0.87,
            "expr_score":  0.80,
            "indicators":  ["arms_raised", "upright"]
        },
        None,
        {
            "status":      "confirmed",
            "confidence":  0.93,
            "priority":    "CRITICAL",
            "expression":  "fear",
            "yolo_score":  0.95,
            "pose_score":  0.94,
            "expr_score":  0.87,
            "indicators":  ["fallen",
                           "active_distress",
                           "both_arms_raised"]
        },
        None, None
    ]
}


class DroneSimulator:
    def __init__(self, drone_id, cfg):
        self.drone_id        = drone_id
        self.lat             = cfg['start_lat']
        self.lon             = cfg['start_lon']
        self.altitude        = cfg['altitude']
        self.battery         = cfg['battery']
        self.speed           = cfg['speed']
        self.heading         = cfg['heading']
        self.radius          = cfg['patrol_radius']
        self.angle           = 0.0
        self.tick            = 0
        self.scenario_idx    = 0
        self.scenarios       = SCENARIOS[drone_id]
        self.detections_today= 0
        self.confirmed_victims=0
        self.connected       = False
        self.client          = None

    def connect(self):
        try:
            self.client = mqtt.Client(
				mqtt.CallbackAPIVersion.VERSION2,
				client_id=self.drone_id)
            self.client.tls_set(
                ca_certs=os.path.join(
                    CERTS_DIR,
                    'AmazonRootCA1.pem'),
                certfile=os.path.join(
                    CERTS_DIR,
                    'af93558c3cfef06d0f17d4cb955d5345b276c76b76baaed3a6f7da5c4858e8c0-certificate.pem.crt'),
                keyfile=os.path.join(
                    CERTS_DIR,
                    'af93558c3cfef06d0f17d4cb955d5345b276c76b76baaed3a6f7da5c4858e8c0-private.pem.key'),
                tls_version=ssl.PROTOCOL_TLSv1_2
            )
            self.client.on_connect = self._on_connect
            self.client.connect(IOT_ENDPOINT, 8883)
            self.client.loop_start()
            time.sleep(3)
            return True
        except Exception as e:
            print(f"  {self.drone_id} connect error: {e}")
            return False

    def _on_connect(self, client,
                    userdata, flags, rc, properties=None):
        if rc == 0:
            self.connected = True
            print(f"  {self.drone_id} connected")
        else:
            print(f"  {self.drone_id} rc={rc}")

    def update_position(self):
        self.angle   += 0.1
        self.lat      = (DRONE_CONFIGS[self.drone_id]
                        ['start_lat'] +
                        self.radius *
                        math.cos(self.angle))
        self.lon      = (DRONE_CONFIGS[self.drone_id]
                        ['start_lon'] +
                        self.radius *
                        math.sin(self.angle))
        self.altitude+= random.uniform(-0.5, 0.5)
        self.altitude = max(30, min(80,
                        self.altitude))
        self.heading  = (math.degrees(self.angle)
                        + 90) % 360
        self.speed   += random.uniform(-0.2, 0.2)
        self.speed    = max(2.0, min(8.0,
                        self.speed))

    def update_battery(self):
        drain         = 0.02 + (self.speed * 0.003)
        self.battery -= drain
        self.battery  = max(0, self.battery)

    def get_battery_health(self):
        if self.battery > 50: return 'GOOD'
        if self.battery > 20: return 'LOW'
        if self.battery > 5:  return 'CRITICAL'
        return 'EMPTY'

    def get_flight_mode(self):
        if self.battery <= 5:  return 'RTH'
        if self.battery <= 20: return 'RTH_WARNING'
        return 'ACTIVE'

    def get_signal(self):
        dist = math.sqrt(
            (self.lat -
             DRONE_CONFIGS[self.drone_id]
             ['start_lat'])**2 +
            (self.lon -
             DRONE_CONFIGS[self.drone_id]
             ['start_lon'])**2
        )
        return int(-50 - (dist * 10000))

    def get_scenario(self):
        s = self.scenarios[
            self.scenario_idx %
            len(self.scenarios)]
        self.scenario_idx += 1
        return s

    def build_payload(self):
        self.update_position()
        self.update_battery()

        scenario = self.get_scenario()
        ts       = datetime.utcnow().isoformat()

        cpu  = (75.0 if scenario
                else 45.0) + random.uniform(-5, 5)
        ram  = 512 + random.uniform(-50, 50)
        temp = 50 + (cpu * 0.3) + \
               random.uniform(-2, 2)

        payload = {
            "device_id":   self.drone_id,
            "drone_id":    self.drone_id,
            "drone_type":  "quadcopter_simulated",
            "mission":     "flood_search_rescue",
            "simulated":   True,
            "timestamp":   ts,

            "flight": {
                "mode":         self.get_flight_mode(),
                "altitude_m":   round(self.altitude, 2),
                "speed_ms":     round(self.speed, 2),
                "heading_deg":  round(self.heading, 1),
                "is_airborne":  self.battery > 5,
                "flight_time_s":self.tick * INTERVAL
            },

            "location": {
                "lat":          round(self.lat, 6),
                "lon":          round(self.lon, 6),
                "gps_fix":      True,
                "gps_accuracy": round(
                    random.uniform(1.5, 4.0), 1)
            },

            "power": {
                "battery_pct":  round(
                    self.battery, 1),
                "battery_health": self.get_battery_health(),
                "voltage_v":    round(
                    9.0 + (self.battery * 0.02), 2),
                "current_a":    round(
                    6.0 + (self.speed * 0.4), 2),
                "estimated_flight_time_remaining":
                    int(self.battery * 0.6)
            },

            "comms": {
                "signal_dbm":      self.get_signal(),
                "mqtt_connected":  True,
                "packet_loss_pct": round(
                    random.uniform(0, 2.0), 1),
                "latency_ms":      random.randint(
                    20, 80)
            },

            "sensors": {
                "camera_active":     True,
                "yolo_loaded":       True,
                "pose_loaded":       True,
                "expression_loaded": True,
                "temperature_c":     round(temp, 1),
                "cpu_usage_pct":     round(cpu, 1),
                "ram_used_mb":       round(ram, 1),
                "camera_fps":        round(
                    random.uniform(8, 15), 1)
            },

            "environment": {
                "flood_area":     True,
                "visibility":     random.choice(
                    ["clear", "clear", "hazy"]),
                "wind_speed_ms":  round(
                    random.uniform(0, 8), 1),
                "rain_detected":  random.random() < 0.1,
                "water_detected": True
            },

            "mission_stats": {
                "detections_today":  self.detections_today,
                "confirmed_victims": self.confirmed_victims,
                "area_searched_sqm": self.tick * 50,
                "uptime_s":          self.tick * INTERVAL
            }
        }

        if scenario:
            self.detections_today += 1
            if scenario['status'] == 'confirmed':
                self.confirmed_victims += 1

            conf = round(
                scenario['confidence'] +
                random.uniform(-0.02, 0.02), 3)
            payload['detection'] = {
                "status":          scenario['status'],
                "confidence":      conf,
                "priority":        scenario['priority'],
                "class":           "person",
                "victim_confirmed":
                    scenario['status'] == 'confirmed',
                "yolo_score":      round(
                    scenario['yolo_score'] +
                    random.uniform(-0.02, 0.02), 3),
                "pose_score":      round(
                    scenario['pose_score'] +
                    random.uniform(-0.02, 0.02), 3),
                "expression":      scenario['expression'],
                "expression_score":round(
                    scenario['expr_score'] +
                    random.uniform(-0.02, 0.02), 3),
                "pose_indicators": scenario['indicators'],
                "indicators":      scenario['indicators'],
                "requires_review":
                    scenario['status'] == 'uncertain',
                "threshold_used":  0.60,
                "floor_used":      0.30
            }
        else:
            payload['status']    = 'scanning'
            payload['detection'] = None

        self.tick += 1
        return payload

    def run(self):
        print(f"\nStarting {self.drone_id}...")
        self.connect()

        topic = (f"mosaic/node/"
                 f"{self.drone_id}/detection")

        while True:
            try:
                payload  = self.build_payload()
                msg      = json.dumps(payload)
                det      = payload.get('detection')

                if self.connected:
                    self.client.publish(
                        topic, msg, qos=1)
                    log_to_csv(self.drone_id, payload)
                    status_icon = 'ok'
                else:
                    status_icon = 'not ok'
                
                log_telemetry(payload)
                if payload.get('detection'):log_detection(payload)
                else:log_heartbeat(payload)

                if det:
                    print(
                        f"  [{status_icon}] "
                        f"{self.drone_id} | "
                        f"batt={payload['power']['battery_pct']:.0f}% | "
                        f"{det['status'].upper()} "
                        f"conf={det['confidence']:.2f} "
                        f"priority={det['priority']}"
                    )
                else:
                    print(
                        f"  [{status_icon}] "
                        f"{self.drone_id} | "
                        f"batt={payload['power']['battery_pct']:.0f}% | "
                        f"SCANNING "
                        f"alt={payload['flight']['altitude_m']}m"
                    )

            except Exception as e:
                print(f"  {self.drone_id} error: {e}")

            time.sleep(INTERVAL)


def main():
    print("\n" + "="*60)
    print("  MOSAIC Swarm Simulator")
    print("  Simulating: node-02, node-03, node-04")
    print(f"  Endpoint: {IOT_ENDPOINT}")
    print(f"  Certs dir: {CERTS_DIR}")
    print(f"  Interval: {INTERVAL}s")
    print("="*60 + "\n")

    simulators = []
    threads    = []

    for drone_id, cfg in DRONE_CONFIGS.items():
        sim = DroneSimulator(drone_id, cfg)
        simulators.append(sim)
        t = threading.Thread(
            target=sim.run,
            daemon=True,
            name=drone_id
        )
        threads.append(t)

    print("Connecting all nodes...")
    for t in threads:
        t.start()
        time.sleep(1)

    print(f"\nAll {len(threads)} simulators running")
    print("Press Ctrl+C to stop\n")
    print("-"*60)

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nSimulator stopped")


if __name__ == "__main__":
    main()
