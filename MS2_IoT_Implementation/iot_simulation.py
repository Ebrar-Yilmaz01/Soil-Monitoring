import csv
import json
import time
import random
import os
import paho.mqtt.client as mqtt


CSV_PATH = os.getenv('CSV_PATH', '/app/Crop_recommendation.csv')
SEND_INTERVAL = int(os.getenv('SEND_INTERVAL', 5))
BROKER = os.getenv('BROKER', "broker.hivemq.com")
PORT = int(os.getenv('PORT', 1883))
TOPIC = os.getenv('TOPIC', "farm/data")


DEVICES = [
    "device_germany",
    "device_england",
    "device_india",
    "device_egypt",
    "device_brazil"
]


NUM_DEVICES = len(DEVICES)


def add_noise(value, std):
    return value + random.gauss(0, std)


def clamp(value, mn, mx):
    return max(mn, min(mx, value))


def load_dataset():
    rows = []
    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row.pop("label", None)
            for k in row:
                row[k] = float(row[k])
            rows.append(row)
    return rows


def apply_noise(row):
    return {
        "N": clamp(add_noise(row["N"], 5), 0, 200),
        "P": clamp(add_noise(row["P"], 5), 0, 200),
        "K": clamp(add_noise(row["K"], 5), 0, 250),
        "temperature": clamp(add_noise(row["temperature"], 1.5), -10, 50),
        "humidity": clamp(add_noise(row["humidity"], 3), 0, 100),
        "ph": clamp(add_noise(row["ph"], 0.3), 0, 14),
        "rainfall": clamp(add_noise(row["rainfall"], 10), 0, 500)
    }


def main():
    client = mqtt.Client()
    client.connect(BROKER, PORT, 60)
    client.loop_start()
    rows = load_dataset()
    total_rows = len(rows)
    index = 0

    print(f"[INFO] Loaded {total_rows} rows from CSV.")
    print(f"[INFO] Connected to MQTT broker: {BROKER}")
    print(f"[INFO] Publishing to topic: {TOPIC}")
    print(f"[INFO] Send interval: {SEND_INTERVAL}s\n")

    while True:
        device_id = DEVICES[index % NUM_DEVICES]
        row = rows[index % total_rows]
        noisy = apply_noise(row)
        payload = {
            "device_id": device_id,
            "timestamp": time.time(),
            **noisy
        }
        msg = json.dumps(payload)

        print("==============================")
        print(f"[MQTT] Publishing {device_id}")
        print(msg)
        print("==============================\n")

        client.publish(TOPIC, msg)
        index += 1
        time.sleep(SEND_INTERVAL)


if __name__ == "__main__":
    main()
