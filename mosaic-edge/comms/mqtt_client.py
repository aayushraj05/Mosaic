# comms/mqtt_client.py
import json
import ssl
import os
import sys
sys.path.append(
    os.path.dirname(os.path.dirname(__file__)))
import config

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except Exception:
    MQTT_AVAILABLE = False


class MQTTClient:
    def __init__(self, on_policy_received):
        self.on_policy_received = on_policy_received
        self.client             = None
        self.connected          = False

    def connect(self):
        if not MQTT_AVAILABLE:
            print("MQTT not available")
            return
        try:
            self.client = mqtt.Client(
                mqtt.CallbackAPIVersion.VERSION2,
                client_id=config.DEVICE_ID)
            self.client.tls_set(
                ca_certs=os.path.join(
                    config.CERTS_DIR,
                    'AmazonRootCA1.pem'),
                certfile=os.path.join(
                    config.CERTS_DIR,
                    'af93558c3cfef06d0f17d4cb955d5345b276c76b76baaed3a6f7da5c4858e8c0-certificate.pem.crt'),
                keyfile=os.path.join(
                    config.CERTS_DIR,
                    'af93558c3cfef06d0f17d4cb955d5345b276c76b76baaed3a6f7da5c4858e8c0-private.pem.key'),
                tls_version=ssl.PROTOCOL_TLSv1_2
            )
            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            self.client.connect(
                config.IOT_ENDPOINT, 8883)
            self.client.loop_start()
            print("MQTT connecting...")
        except Exception as e:
            print(f"MQTT connect error: {e}")

    def _on_connect(self, client, userdata,
                    flags, rc, properties=None):
        if rc == 0:
            self.connected = True
            print("MQTT connected to IoT Core")
            self.client.subscribe(
                f"mosaic/node/"
                f"{config.DEVICE_ID}/policy")
            self.client.subscribe(
                f"mosaic/node/"
                f"{config.DEVICE_ID}/command")
        else:
            print(f"MQTT connect failed rc={rc}")

    def _on_message(self, client,
                    userdata, msg):
        try:
            payload = json.loads(
                msg.payload.decode())
            print(f"MQTT received: {msg.topic}")
            if 'threshold' in payload:
                self.on_policy_received(payload)
        except Exception as e:
            print(f"MQTT message error: {e}")

    def publish_detection(self, payload):
        try:
            if not self.connected:
                print("MQTT not connected"
                      " skipping publish")
                return

            topic = (f"mosaic/node/"
                     f"{config.DEVICE_ID}"
                     f"/detection")

            msg = json.dumps(
                payload, default=str)

            self.client.publish(
                topic, msg, qos=1)

            # Safe status logging
            detection = payload.get('detection')
            if detection:
                status = detection.get(
                    'status', 'unknown')
            else:
                status = payload.get(
                    'status', 'heartbeat')

            print(f"Published: {status}"
                  f" {topic}")

        except KeyError as e:
            print(f"Publish key error: {e}")
            print(f"Payload keys: "
                  f"{list(payload.keys())}")
        except Exception as e:
            print(f"Publish error: {e}")

    def publish_heartbeat(self):
        from datetime import datetime
        payload = {
            'device_id': config.DEVICE_ID,
            'drone_id':  config.DEVICE_ID,
            'timestamp': datetime.utcnow(
                         ).isoformat(),
            'status':    'scanning',
            'detection': None
        }
        self.publish_detection(payload)

    def disconnect(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            print("MQTT disconnected")
