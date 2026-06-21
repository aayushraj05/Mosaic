# MOSAIC

## Modular Orchestrated Swarm with Adaptive Intelligence and Coordination

**AI-powered autonomous drone swarm system for flood disaster search and rescue operations.**

MOSAIC combines Edge AI, cloud intelligence, and human-in-the-loop learning to detect flood victims, coordinate rescue teams, and continuously improve decision-making across multiple drones in real time.

---

## Overview

During flood disasters, rescue teams often struggle to locate victims quickly due to limited visibility, inaccessible terrain, and communication challenges.

MOSAIC addresses these challenges through a coordinated swarm of intelligent drones capable of:

* Autonomous aerial surveillance
* Real-time victim detection
* Distress behavior analysis
* GPS-based location reporting
* Adaptive learning from operator feedback
* Multi-drone intelligence synchronization

The system is designed to identify victims and deliver actionable rescue information to response teams in **under 3 seconds**.

---

## Key Features

### Autonomous Drone Swarm

* Deploys a coordinated fleet of 4 drones
* Covers large flood-affected regions efficiently
* Shares intelligence across all active nodes

### Edge AI Victim Detection

* YOLOv8-based real-time person detection
* Runs directly on Raspberry Pi 4
* Reduces cloud dependency and latency

### Distress Recognition

* Human pose analysis for emergency gestures
* Confidence-based risk assessment
* Enhanced victim prioritization

### Rapid Rescue Coordination

* Automatic GPS coordinate extraction
* Detection data transmitted in under 3 seconds
* Immediate rescue team notification

### Human-in-the-Loop Learning

* Operators review uncertain detections
* Feedback continuously improves system accuracy
* Decision thresholds adapt dynamically

### Dual Dashboard Architecture

* Operator Dashboard for incident review
* Command Dashboard for mission monitoring
* Real-time swarm health and analytics

---

## System Architecture

```text
Flood Disaster Zone
        │
        ▼
┌────────────────────────┐
│   Drone Swarm Layer    │
│    (4 AI Drones)       │
└────────────────────────┘
        │
        ▼
┌────────────────────────┐
│  Edge AI Processing    │
│ YOLOv8 + Pose Analysis │
└────────────────────────┘
        │
        ▼
┌────────────────────────┐
│       AWS Cloud        │
│ IoT • Lambda • DynamoDB│
└────────────────────────┘
        │
   ┌────┴────┐
   ▼         ▼
Operator  Command
Dashboard Dashboard
```

---

# Hardware Requirements

## Compute

| Component | Specification                    |
| --------- | -------------------------------- |
| SBC       | Raspberry Pi 4 Model B (8GB RAM) |
| Storage   | 64GB Class-10 MicroSD Card       |

## Camera

| Component     | Specification                   |
| ------------- | ------------------------------- |
| Camera Module | Raspberry Pi Camera Module v1.3 |
| Sensor        | OV5647                          |
| Interface     | CSI Ribbon Cable                |

## Drone Platform

| Component                    | Quantity |
| ---------------------------- | -------- |
| F450 Frame                   | 1        |
| Avionics C2826 1000KV Motors | 4        |
| 30A ESC                      | 4        |
| 10x4.5 Propellers            | 4        |

## Power

| Component          | Specification               |
| ------------------ | --------------------------- |
| Flight Battery     | 3S LiPo 3300mAh 35C         |
| Connector          | XT60                        |
| Raspberry Pi Power | 5V 3A USB-C                 |
| Test Power Supply  | Keithley DC Supply (11V 3A) |

## Cooling

| Component   | Specification |
| ----------- | ------------- |
| Heatsinks   | Aluminum Set  |
| Cooling Fan | 30mm 5V Fan   |

---

# Software Stack

## Operating System

* Raspberry Pi OS Trixie (Debian 13)
* Python 3.13.5

## AI & Computer Vision

* YOLOv8
* OpenCV
* NumPy
* Pillow

## AWS Services

* AWS IoT Core
* AWS Lambda
* Amazon DynamoDB
* Amazon S3
* Amazon API Gateway
* Amazon CloudWatch

---

# AWS Infrastructure

## AWS IoT Core

### Device

```yaml
Thing Name: mosaic-node-01
Protocol: MQTT over TLS
Purpose: Detection and Telemetry Communication
```

---

## DynamoDB Tables

| Table            | Purpose                     |
| ---------------- | --------------------------- |
| detections       | Victim detection records    |
| swarm_nodes      | Drone health and status     |
| policies         | Adaptive threshold policies |
| feedback_history | Operator feedback logs      |

---

## S3 Bucket

```yaml
Bucket Name: mosaic-snapshots-yourname
Region: ap-south-1
Purpose: Detection image storage
```

---

## Lambda Functions

| Function                 | Responsibility         |
| ------------------------ | ---------------------- |
| mosaic-detection-ingest  | Detection processing   |
| mosaic-operator-feedback | Feedback learning      |
| mosaic-get-detections    | Detection retrieval    |
| mosaic-get-swarm-status  | Swarm monitoring       |
| mosaic-get-policy        | Policy synchronization |
| mosaic-heartbeat-ingest  | Health monitoring      |
| mosaic-get-scenarios     | Scenario simulation    |

---

## API Gateway Endpoints

```text
/detections
/feedback
/swarm
/policy
/heartbeat
/scenarios
```

All endpoints are deployed to the **dev** stage with CORS enabled.

---

# Project Structure

```text
mosaic-edge/
│
├── actuation/
│   ├── __init__.py
│   └── motor_controller.py
│
├── camera/
│   ├── __init__.py
│   └── capture.py
│
├── certs/
│   └── README.md
│
├── comms/
│   ├── __init__.py
│   └── mqtt_client.py
│
├── data/
│   └── .gitkeep
│
├── detection/
│   ├── __init__.py
│   ├── confidence.py
│   ├── detector.py
│   ├── expression_analyzer.py
│   └── pose_analyzer.py
│
├── lambda/
│   └── (7 Lambda Functions)
│
├── models/
│   └── README.md
│
├── utils/
│   ├── __init__.py
│   ├── image_utils.py
│   └── telemetry_logger.py
│
├── config.example.py
├── dashboard.html
├── stakeholder.html
├── env_setup.py
├── esc_calibrate.py
├── swarm_simulator.py
├── download_models.py
├── motor_diagnostic.py
├── throttle_test.py
├── launch_all.sh
├── main.py
├── requirements.txt
└── adaptive_rules.json
```

---

# Performance Targets

| Metric                  | Target         |
| ----------------------- | -------------- |
| Detection Response Time | < 3 Seconds    |
| Drone Fleet Size        | 4 Nodes        |
| Edge Processing         | Real-Time      |
| Cloud Synchronization   | Near Real-Time |
| Dashboard Updates       | Live           |
| Learning Mode           | Adaptive       |

---

# Innovation Highlights

* Autonomous Multi-Drone Coordination
* Edge AI Victim Detection
* Human-in-the-Loop Learning
* Adaptive Confidence Thresholds
* Real-Time GPS Rescue Alerts
* Cloud-Synchronized Swarm Intelligence
* Dual Dashboard Command Architecture

---

# Future Enhancements

* GPS-guided autonomous navigation
* Thermal camera integration
* Multi-class disaster victim detection
* AI-based route optimization
* Mesh networking between drones
* Large-scale swarm deployment

---

# Mission Statement

> **MOSAIC aims to accelerate flood disaster response through autonomous drone swarms, edge artificial intelligence, and adaptive human-guided learning to locate victims faster, improve rescue efficiency, and ultimately save lives.**

---

## Authors

**Aayush Rajput**

**Product:** MOSAIC – Flood Disaster Response System
