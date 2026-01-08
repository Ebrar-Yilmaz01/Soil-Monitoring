import json
import time
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
TOPIC_EU = "farm/cloud/europe/alerts"
TOPIC_ASIA = "farm/cloud/asia/alerts"
client = mqtt.Client()
client.connect(BROKER, 1883, 60)

def mock_event(device_id, region, param, value, severity):
    return {
        "edge_node": f"edge-{region}",
        "timestamp": time.time(),
        "device_id": device_id,
        "anomaly_result": {
            "parameter": param,
            "value": value,
            "severity": severity,
            "anomalies_detected": [
                {"method": "threshold", "message": f"{param} too {severity}"}
            ]
        }
    }

while True:
    event = mock_event(
        device_id="device_germany",
        region="europe",
        param="temperature",
        value=45.2,
        severity="high"
    )

    msg = json.dumps(event)
    client.publish(TOPIC_EU, msg)
    print("[MOCK] Sent:", msg)
    time.sleep(20)