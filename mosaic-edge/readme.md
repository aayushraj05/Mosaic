# MOSAIC
## Modular Orchestrated Swarm with Adaptive Intelligence and Coordination

AI-powered drone swarm system for flood disaster search and rescue operations.
Detects flood victims autonomously using YOLOv8, sends GPS coordinates to
rescue teams in under 3 seconds, and adapts through human-in-the-loop learning.

---

## What This System Does

- Deploys 4 autonomous drones over flood-affected area
- Detects persons in real time using YOLOv8 AI on Raspberry Pi 4
- Analyzes body pose to identify distress signals
- Sends GPS coordinates to rescue teams in under 3 seconds
- Operator reviews uncertain detections with actual photos
- System threshold adapts based on operator feedback
- All 4 drones receive updated intelligence simultaneously
- Two dashboards serve operators and commanders separately

---

## Hardware Required

### Compute
- Raspberry Pi 4 Model B 8GB RAM
- MicroSD Card 64GB Class 10 minimum

### Camera
- Raspberry Pi Camera Module v1.3 (OV5647 sensor)
- CSI ribbon cable

### Drone Frame and Motors
- F450 Quadcopter Frame with built-in PDB
- 4x Avionics C2826 1000KV Brushless Motors
- 4x 30A ESC (Electronic Speed Controllers)
- 4x 10x4.5 inch Propellers (2 CW, 2 CCW)

### Power
- 3S LiPo Battery 3300mAh 35C (XT60 connector)
- USB-C 5V 3A adapter for Raspberry Pi (separate)
- OR Keithley DC bench supply 11V 3A for testing

### Cooling
- Aluminum heatsink set for Pi 4
- 30mm 5V cooling fan

### Connections
- Male to Female jumper wires (minimum 10)
- XT60 male connector for battery connection

---

## Software Required

### Operating System
- Raspberry Pi OS Trixie (Debian 13)
- Python 3.13.5 (comes with Trixie)

### AWS Services Required
- AWS Account with ap-south-1 region access
- AWS IoT Core
- AWS Lambda
- AWS DynamoDB
- AWS S3
- AWS API Gateway
- AWS CloudWatch

### Python Libraries
Listed in requirements.txt

---

## AWS Infrastructure Required

### IoT Core
- Thing Name: mosaic-node-01
- IoT Policy: allow all IoT actions
- Certificate: device certificate attached to thing
- IoT Rule: routes detection topic to Lambda 1

### DynamoDB Tables
- detections (PK: device_id, SK: timestamp)
- swarm_nodes (PK: device_id)
- policies (PK: device_id)
- feedback_history (PK: device_id, SK: timestamp)

### S3 Bucket
- Name: mosaic-snapshots-yourname
- Region: ap-south-1
- Public read access for images

### Lambda Functions (7 total)
- mosaic-detection-ingest
- mosaic-operator-feedback
- mosaic-get-detections
- mosaic-get-swarm-status
- mosaic-get-policy
- mosaic-heartbeat-ingest
- mosaic-get-scenarios

### API Gateway
- REST API with 6 endpoints
- CORS enabled on all resources
- Deployed to stage: dev

### IAM Role
- mosaic-lambda-role
- Permissions: DynamoDB, S3, IoT, Lambda, CloudWatch

---

## Project Structure
mosaic-edge/
├── actuation/              Motor and ESC control
│   ├── init.py
│   └── motor_controller.py
├── camera/                 Camera capture
│   ├── init.py
│   └── capture.py
├── certs/                  AWS IoT certificates
│   └── README.md           (certificates not in repo)
├── comms/                  MQTT communication
│   ├── init.py
│   └── mqtt_client.py
├── data/                   Local telemetry storage
│   └── .gitkeep
├── detection/              AI detection pipeline
│   ├── init.py
│   ├── confidence.py
│   ├── detector.py
│   ├── expression_analyzer.py
│   └── pose_analyzer.py
├── lambda/                 AWS Lambda functions
│   └── (7 Python files)
├── models/                 YOLO model files
│   └── README.md           (models not in repo)
├── utils/                  Helper utilities
│   ├── init.py
│   ├── image_utils.py
│   └── telemetry_logger.py
├── config.example.py       Configuration template
├── dashboard.html          Operator dashboard
├── stakeholder.html        Stakeholder dashboard
├── env_setup.py            Environment variables
├── esc_calibrate.py        ESC calibration tool
├── swarm_simulator.py      Simulates nodes 02 03 04
├── download_models.py      Downloads YOLO models
├── motor_diagnostic.py     Motor testing tool
├── throttle_test.py        Throttle testing tool
├── launch_all.sh           Launches all services
├── main.py                 Main detection loop
├── requirements.txt        Python dependencies
└── adaptive_rules.json     Threshold learning rules