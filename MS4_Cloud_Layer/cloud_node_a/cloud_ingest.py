import json
import requests
import paho.mqtt.client as mqtt
from collections import defaultdict
from anomaly_detector import AnomalyDetector


BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "farm/cloud/#"
AKKA_ENDPOINT = "http://localhost:8080/alert"


class CloudIngestion:
    def __init__(self):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_message = self.on_message
        
        # Initialize anomaly detector
        self.detector = AnomalyDetector(
            zscore_threshold=2.5,
            iqr_multiplier=1.5,
            change_rate_threshold=0.3,
            window_size=20
        )
        
        # Store baseline values per device/parameter
        # Format: {device_id: {parameter: [value1, value2, ...]}}
        self.baselines = defaultdict(lambda: defaultdict(list))
        
        # Store previous values for change rate detection
        # Format: {device_id: {parameter: value}}
        self.previous_values = defaultdict(dict)
        
        # Critical thresholds (customize für deine Sensoren)
        self.critical_thresholds = {
            "N": {"low": 0, "high": 100},      # Stickstoff (mg/kg)
            "P": {"low": 0, "high": 80},       # Phosphor (mg/kg)
            "K": {"low": 0, "high": 400},      # Kalium (mg/kg)
            "pH": {"low": 4.0, "high": 8.5},   # pH-Wert
            "moisture": {"low": 10, "high": 80},  # Bodenfeuchte (%)
            "temperature": {"low": -10, "high": 50}  # Temperatur (°C)
        }
    
    def _update_baseline(self, device_id: str, parameter: str, value: float):
        """
        Update baseline values for anomaly detection
        Keep only last N values (sliding window)
        """
        baseline = self.baselines[device_id][parameter]
        baseline.append(value)
        
        # Keep only last 20 readings
        if len(baseline) > 20:
            baseline.pop(0)
    
    def _get_baseline(self, device_id: str, parameter: str) -> list:
        """Get baseline values for a device/parameter"""
        baseline = self.baselines[device_id][parameter]
        return list(baseline) if baseline else []
    
    def _get_previous_value(self, device_id: str, parameter: str) -> float:
        """Get previous value for change rate detection"""
        return self.previous_values[device_id].get(parameter)
    
    def _set_previous_value(self, device_id: str, parameter: str, value: float):
        """Store previous value"""
        self.previous_values[device_id][parameter] = value
    
    def _get_critical_thresholds(self, parameter: str) -> dict:
        """Get critical thresholds for parameter"""
        return self.critical_thresholds.get(parameter, {})
    
    def on_message(self, client, userdata, msg):
        try:
            # Parse incoming MQTT message
            alert = json.loads(msg.payload.decode())
            print(f"\n[Cloud A] Received alert from Edge:")
            print(f"  Device: {alert.get('device_id')}")
            print(f"  Data: {alert}")
            
            device_id = alert.get("device_id")
            
            # Extract sensor readings (all keys except metadata)
            metadata_keys = {"edge_node", "device_id", "timestamp"}
            sensor_data = {
                k: v for k, v in alert.items() 
                if k not in metadata_keys
            }
            
            # Anomaly detection per parameter
            anomalies_found = []
            alert_with_anomalies = alert.copy()
            alert_with_anomalies["anomaly_analysis"] = {}
            
            for parameter, current_value in sensor_data.items():
                # Get detection parameters
                baseline = self._get_baseline(device_id, parameter)
                previous_value = self._get_previous_value(device_id, parameter)
                thresholds = self._get_critical_thresholds(parameter)
                
                # Run anomaly detection
                anomaly_result = self.detector.detect_anomalies(
                    current_value=current_value,
                    parameter=parameter,
                    baseline_values=baseline,
                    previous_value=previous_value,
                    critical_low=thresholds.get("low"),
                    critical_high=thresholds.get("high")
                )
                
                # Store result
                alert_with_anomalies["anomaly_analysis"][parameter] = anomaly_result
                
                # Track if anomalies found
                if not self.detector.is_normal(anomaly_result):
                    anomalies_found.append({
                        "parameter": parameter,
                        "severity": anomaly_result["severity"],
                        "details": anomaly_result["anomalies_detected"]
                    })
                
                # Update baselines for next iteration
                self._update_baseline(device_id, parameter, current_value)
                self._set_previous_value(device_id, parameter, current_value)
            
            # Log anomaly summary
            if anomalies_found:
                print(f"\n[Cloud A] ⚠️  ANOMALIES DETECTED for {device_id}:")
                for anom in anomalies_found:
                    print(f"  • {anom['parameter']}: {anom['severity']} - {anom['details']}")
            else:
                print(f"[Cloud A] ✓ All parameters normal for {device_id}")
            
            # Forward to Akka if anomalies detected (sensitivity: medium)
            should_forward = any(
                self.detector.should_forward_to_cloud(
                    alert_with_anomalies["anomaly_analysis"][param],
                    sensitivity="medium"
                )
                for param in sensor_data.keys()
            )
            
            if should_forward or anomalies_found:
                print(f"[Cloud A] → Forwarding anomaly alert to Akka...")
                try:
                    res = requests.post(AKKA_ENDPOINT, json=alert_with_anomalies)
                    print(f"[Cloud A] ✓ Forwarded to Akka, status = {res.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"[Cloud A] ✗ Failed to forward to Akka: {e}")
            else:
                # Normal reading - optional: still forward or store in DynamoDB
                print(f"[Cloud A] → Normal reading (not forwarding)")
                # Hier könnte Optional auch DynamoDB schreiben statt zu Akka
        
        except json.JSONDecodeError as e:
            print(f"[Cloud A] ERROR parsing JSON: {e}")
        except Exception as e:
            print(f"[Cloud A] ERROR handling message: {e}")
    
    def run(self):
        """Start the MQTT listener"""
        print("[Cloud A] Connecting to MQTT broker...")
        self.mqtt_client.connect(BROKER, PORT, 60)
        print(f"[Cloud A] Subscribing to cloud topic: {TOPIC}")
        self.mqtt_client.subscribe(TOPIC)
        print("[Cloud A] Listening for Edge → Cloud messages...\n")
        self.mqtt_client.loop_forever()


def main():
    cloud = CloudIngestion()
    cloud.run()


if __name__ == "__main__":
    main()
