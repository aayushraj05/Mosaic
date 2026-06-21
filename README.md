<div align="center">

<img src="https://img.shields.io/badge/MOSAIC-AI%20Swarm%20Intelligence-00d4ff?style=for-the-badge&labelColor=030810&color=00d4ff" alt="MOSAIC"/>

# 🛸 MOSAIC
### Modular Orchestrated Swarm with Adaptive Intelligence and Coordination

<p align="center">
  <strong>AI-powered drone swarm that finds flood victims 12× faster than manual search</strong><br/>
  Autonomous detection · Cloud pipeline · Human-in-the-loop learning · Dual dashboards
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13.5-3776AB?style=flat-square&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/YOLOv8-Detection-FF6B35?style=flat-square"/>
  <img src="https://img.shields.io/badge/AWS-IoT%20Core-FF9900?style=flat-square&logo=amazonaws&logoColor=white"/>
  <img src="https://img.shields.io/badge/Raspberry%20Pi-4%208GB-C51A4A?style=flat-square&logo=raspberrypi&logoColor=white"/>
  <img src="https://img.shields.io/badge/Status-MVP%20Complete-00ff88?style=flat-square"/>
</p>

<br/>

> **"Turning Critical Minutes into Saved Lives"**  
> *From detection to rescue coordination — in real time*

</div>

---

## 🖼️ System Overview

<div align="center">
  <img src="Images/Physical%20Mvp%20Drone.png" alt="MOSAIC Physical MVP Drone" width="45%"/>
  &nbsp;&nbsp;
  <img src="Images/Operator_dashboard.png" alt="MOSAIC Operator Dashboard" width="45%"/>
</div>

<br/>

<div align="center">
  <img src="Images/Detected_victim%20(Drone%20Pov).png" alt="MOSAIC Live Detection — Drone POV" width="45%"/>
  &nbsp;&nbsp;
  <img src="Images/Rescueteam_dashboard.png" alt="MOSAIC Rescue Team Dashboard" width="45%"/>
</div>

<br/>

<div align="center">
  <img src="Images/Results.png" alt="MOSAIC Detection Results" width="92%"/>
</div>

---

## 🎬 Demo Video

<div align="center">

[![MOSAIC Full System Demo](https://img.youtube.com/vi/-SGyDQs7yAI/maxresdefault.jpg)](https://youtu.be/-SGyDQs7yAI)

**[▶ Watch Full Demo on YouTube](https://youtu.be/-SGyDQs7yAI)**

*Live YOLOv8 detection · Motors spinning · Dashboard updating in real time · Operator feedback · Threshold adapting*

<br/>

📥 **[Download Full Demo Package from Google Drive](https://drive.google.com/drive/folders/1bEV4gVOkEiWBHRMurLpmcDrqar1YKICs?usp=drive_link)**

</div>

---

## 🌊 The Problem

Every year floods in India displace **40 million people** and claim **1,600+ lives** — not because rescue teams are slow, but because nobody knows where victims are.

Manual search teams cover **0.2 sq km/hour**. MOSAIC covers **2.4 sq km/hour per drone**.  
That is **12× faster**. Every second saved is a life saved.

---

## ✨ What MOSAIC Does

| Capability | Detail |
|-----------|--------|
| 🎯 **Autonomous Detection** | YOLOv8 detects persons at 15 FPS on edge hardware |
| 🦾 **Pose Analysis** | 17 body keypoints identify fallen, waving, unconscious victims |
| ☁️ **Cloud Pipeline** | GPS coordinates reach rescue teams in under 3 seconds |
| 🧠 **Adaptive Learning** | Operator feedback updates all drones simultaneously |
| 📊 **Dual Dashboards** | Separate views for technical operators and field commanders |
| 📡 **Resilient Comms** | Works offline — zero data loss architecture |

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    EDGE LAYER (Raspberry Pi 4)                  │
│  Camera → YOLOv8 → Pose Analysis → Confidence Score → Decision │
│  CONFIRMED ≥0.60 | UNCERTAIN 0.30-0.60 | MISSED <0.30         │
└─────────────────────┬───────────────────────────────────────────┘
                      │ MQTT over TLS 1.2
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CLOUD LAYER (AWS ap-south-1)                   │
│  IoT Core → Lambda ×7 → DynamoDB → S3 → API Gateway           │
└─────────────────────┬───────────────────────────────────────────┘
                      │ REST API HTTPS
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COMMAND LAYER (Dashboards)                   │
│  Operator Dashboard ← Same API → Stakeholder Dashboard         │
│  (Technical review)              (GPS + Priority + Maps)       │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Key Performance Metrics

<div align="center">

| Metric | MVP Value | Product Target |
|--------|-----------|----------------|
| Detection Speed | **0.07 sec/frame** | 0.03 sec/frame |
| Detection Accuracy | **85–90%** | 91–95% |
| GPS Precision | Configurable | 1–2 meters |
| Data Latency | **< 3 seconds** | < 1 second |
| Drones per Operator | **4** | 16 |
| Area per Charge | **2.4 sq km** | 4.8 sq km |
| vs Manual Search | **12× faster** | 25× faster |
| False Positive Rate | Starting 25% → **8%** | Starting 8% → 1% |

</div>

---

## 🔧 Hardware Required

<details>
<summary><strong>Click to expand hardware list</strong></summary>

### Compute
- Raspberry Pi 4 Model B — 8GB RAM
- MicroSD Card — 64GB Class 10 minimum

### Camera
- Raspberry Pi Camera Module v1.3 (OV5647 sensor)
- CSI ribbon cable

### Drone Frame and Motors
- F450 Quadcopter Frame with built-in PDB
- 4× Avionics C2826 1000KV Brushless Motors
- 4× 30A ESC (Electronic Speed Controllers)
- 4× 10×4.5 inch Propellers (2 CW, 2 CCW)

### Power
- 3S LiPo Battery 3300mAh 35C (XT60 connector)
- USB-C 5V 3A adapter for Raspberry Pi (separate from drone power)
- OR Keithley DC bench supply 11V 3A for ground testing

### Cooling
- Aluminum heatsink set for Pi 4
- 30mm 5V cooling fan

### Connections
- Male to Female jumper wires × 10 minimum
- XT60 male connector for battery/PDB connection

</details>

---

## ☁️ AWS Infrastructure Required

<details>
<summary><strong>Click to expand AWS setup</strong></summary>

**Region: ap-south-1 (Mumbai)**

| Service | Resource | Purpose |
|---------|----------|---------|
| **IoT Core** | Thing: mosaic-node-01 | MQTT broker for drone communication |
| **IoT Core** | Rule: mosaic-detection-rule | Routes detections to Lambda |
| **Lambda** | mosaic-detection-ingest | Processes drone detections |
| **Lambda** | mosaic-operator-feedback | Handles operator confirm/reject |
| **Lambda** | mosaic-get-detections | Serves detection data to dashboard |
| **Lambda** | mosaic-get-swarm-status | Serves drone status to dashboard |
| **Lambda** | mosaic-get-policy | Returns adaptive threshold |
| **Lambda** | mosaic-heartbeat-ingest | Records drone heartbeats |
| **Lambda** | mosaic-get-scenarios | Returns demo scenario data |
| **DynamoDB** | detections | Stores all detection events |
| **DynamoDB** | swarm_nodes | Stores drone status |
| **DynamoDB** | policies | Stores adaptive thresholds |
| **DynamoDB** | feedback_history | Stores operator feedback |
| **S3** | mosaic-snapshots-* | Stores uncertain detection images |
| **API Gateway** | /detections /swarm /policy /feedback /heartbeat /scenarios | REST API for dashboards |
| **IAM** | mosaic-lambda-role | Lambda execution permissions |

</details>

---

## 🚀 Quick Start

### Prerequisites
```bash
# Raspberry Pi OS Trixie (Debian 13) with Python 3.13.5
# AWS Account with ap-south-1 access
```

### 1 — System Packages
```bash
sudo apt update
sudo apt install -y python3-picamera2 python3-libcamera python3-kms++
```

### 2 — Python Libraries
```bash
pip install -r requirements.txt --break-system-packages
```

### 3 — Download AI Models
```bash
python3 download_models.py
```

### 4 — Configure
```bash
cp config.example.py config.py
nano config.py
# Set IOT_ENDPOINT, GPS_LAT, GPS_LON
```

### 5 — Add AWS Certificates
```
Place in certs/ folder:
  AmazonRootCA1.pem
  device.pem.crt
  private.pem.key
```

### 6 — Run
```bash
# Terminal 1 — Main detection system
python3 main.py

# Terminal 2 — Swarm simulator (nodes 02, 03, 04)
python3 swarm_simulator.py

# Dashboard — open in browser
python3 -m http.server 3000
# http://localhost:3000/dashboard.html
```

> 📖 See **[SETUP.txt](SETUP.txt)** for complete step-by-step setup from scratch including all AWS configuration.

---

## 📁 Project Structure

```
mosaic-edge/
├── 🤖 actuation/           Motor and ESC control (F450 brushless)
├── 📷 camera/              picamera2 capture with fallback modes
├── 🔐 certs/               AWS IoT certificates (not in repo)
├── 📡 comms/               MQTT client with auto-reconnect
├── 💾 data/                Local telemetry CSV storage
├── 🧠 detection/           AI pipeline — YOLOv8 + Pose + Expression
├── ☁️  lambda/              7 AWS Lambda functions
├── 🖼️  Images/              Product screenshots and drone photos
├── 🤖 models/              YOLO model files (not in repo)
├── 🛠️  utils/               Image drawing and telemetry logging
├── ⚙️  config.example.py    Configuration template (copy to config.py)
├── 📊 dashboard.html        Operator dashboard — real-time detection review
├── 👥 stakeholder.html      Commander dashboard — GPS victim list
├── 🚀 main.py              Main autonomous detection loop
├── 🐝 swarm_simulator.py   Simulates drone nodes 02, 03, 04
├── 🔧 esc_calibrate.py     First-time ESC calibration tool
├── 📋 requirements.txt     Python dependencies
└── 📖 SETUP.txt            Complete setup guide from scratch
```

---

## 🔄 Detection Pipeline

```
Camera Frame (640×480 @ 15FPS)
         │
         ▼
┌─────────────────┐
│   YOLOv8n       │  → Person detected     weight: 50%
└────────┬────────┘
         ▼
┌─────────────────┐
│  Pose Analysis  │  → 17 keypoints        weight: 30%
│  YOLOv8n-Pose   │    fallen/waving/unconscious
└────────┬────────┘
         ▼
┌─────────────────┐
│   Expression    │  → OpenCV Haar Cascade weight: 20%
│   Analysis      │
└────────┬────────┘
         ▼
  Final Score = YOLO×0.50 + Pose×0.30 + Expression×0.20
         │
         ├── ≥ 0.60  →  ✅ CONFIRMED  → Motors spin + GPS sent to cloud
         ├── ≥ 0.30  →  ⚠️  UNCERTAIN  → Image sent to operator for review
         └── < 0.30  →  ❓ MISSED     → Logged locally + rescan triggered
```

---

## 🧠 Adaptive Learning Loop

```
Detection → Uncertain → Operator sees photo
                              │
                    ┌─────────┴──────────┐
                    ▼                    ▼
             CONFIRM VICTIM        FALSE POSITIVE
                    │                    │
                    └─────────┬──────────┘
                              ▼
                    Lambda 2 calculates new threshold
                    FP rate > 40%    → raise +0.05
                    Confirm > 70%    → lower -0.03
                              │
                              ▼
                    MQTT pushed to ALL 4 drones
                    simultaneously (< 2 seconds)
                              │
                              ▼
                    adaptive_rules.json updated
                    Motors pulse = rescan signal
```

---

## 👥 Users and Stakeholders

| Role | Dashboard | Primary Need |
|------|-----------|-------------|
| **Drone Operator** | Operator Dashboard | Review uncertain detections, manage drones |
| **NDRF Commander** | Stakeholder Dashboard | GPS victim locations, dispatch decisions |
| **Field Rescue Team** | Tablet GPS | Navigate directly to victim coordinates |
| **District Official** | Stakeholder Dashboard | Coverage status, victim count, records |

---

## 🛣️ MVP → Product Roadmap

| Component | MVP | Product |
|-----------|-----|---------|
| Compute | Raspberry Pi 4 | NVIDIA Jetson Orin NX |
| Detection | YOLOv8n CPU | YOLOv8x + TensorRT GPU |
| Camera | OV5647 RGB only | Sony IMX477 + FLIR Lepton thermal |
| GPS | Hardcoded config | u-blox M9N (GPS+GLONASS+Galileo+BeiDou) |
| Communication | 4G WiFi only | 4G + LoRa 15km + WiFi mesh + Starlink |
| Learning | Rule-based threshold | Qwen 2.5 LLM contextual adaptation |
| Drones | 1 real + 3 simulated | Up to 16 physical drones |
| Cooling | Heatsink + fan | Active liquid cooling |
| Sensors | Camera only | Wind, temperature, humidity, barometer, air quality |

---

## 👨‍💻 Team

| Name | Employee ID |
|------|-------------|
| Giftina Roseline S N | 2861104 |
| Rishav Kumar | 3199845 |
| Bharanidharan J | 2859059 |
| Oviya P | 2876916 |
| Aayush Rajput | 2861780 |
| Soma Sundaram A | 2860572 |

---

## 🏢 Institution

**TCS — Tata Consultancy Services**  
Project MOSAIC — Flood Disaster Response AI System  
IAE Training Program · 2026

---

<div align="center">

**FROM DETECTION TO RESCUE COORDINATION — IN REAL TIME**

*Designed for Flood Response · Autonomous Operations · Smart Coordination · Scalable Deployment*

<br/>

[![YouTube](https://img.shields.io/badge/Demo-YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtu.be/-SGyDQs7yAI)
[![Google Drive](https://img.shields.io/badge/Download-Google%20Drive-4285F4?style=for-the-badge&logo=googledrive&logoColor=white)](https://drive.google.com/drive/folders/1bEV4gVOkEiWBHRMurLpmcDrqar1YKICs?usp=drive_link)

</div>
