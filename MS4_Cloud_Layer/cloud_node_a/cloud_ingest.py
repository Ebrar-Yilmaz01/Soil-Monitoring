import json
import requests
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "farm/cloud/#"
AKKA_ENDPOINT = "http://localhost:8080/alert"

def on_message(client, userdata, msg):
    try:
        alert = json.loads(msg.payload.decode())
        print("\n[Cloud A] Received alert from Edge:")
        print(alert)
        res = requests.post(AKKA_ENDPOINT, json=alert)
        print("[Cloud A] Forwarded to Cloud Node B, status =", res.status_code)

    except Exception as e:
        print("[Cloud A] ERROR handling message:", e)

def main():
    client = mqtt.Client()
    client.on_message = on_message

    print("[Cloud A] Connecting to MQTT broker...")
    client.connect(BROKER, PORT, 60)
    print(f"[Cloud A] Subscribing to cloud topic: {TOPIC}")
    client.subscribe(TOPIC)
    print("[Cloud A] Listening for Edge → Cloud messages...")
    client.loop_forever()

if __name__ == "__main__":
    main()
