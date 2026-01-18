#!/usr/bin/env python3
"""
Edge Layer Node - Soil Analysis
Forward all sensor data to Cloud (Anomaly Detection moved to Cloud)
"""

import json
import logging
import sys
import time
import signal
import paho.mqtt.client as mqtt

from edge_config import get_edge_node_config
from redis_manager import RedisTimeSeriesManager

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('edge_node.log')
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# EDGE NODE CLASS
# ============================================================================

class EdgeNode:
    """
    Edge Node for Soil Analysis System
    
    Responsibilities (SIMPLIFIED):
    - Receive MQTT messages from IoT devices
    - Store readings in Redis (for reference)
    - Forward ALL data to Cloud for processing
    """
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.config = get_edge_node_config(node_id)
        self.running = False
        
        # Initialize components
        self.redis_manager = None
        self.mqtt_client = None
        self._init_redis()
        self._init_mqtt()
        
        logger.info(f"Edge Node {node_id} initialized successfully")
    
    def _init_redis(self) -> None:
        """Initialize Redis connection"""
        try:
            self.redis_manager = RedisTimeSeriesManager(
                host=self.config.redis_host,
                port=self.config.redis_port,
                db=0
            )
            logger.info(f"✓ Redis connected: {self.config.redis_host}:{self.config.redis_port}")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise
    
    def _init_mqtt(self) -> None:
        """Initialize MQTT client"""
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self._on_mqtt_connect
        self.mqtt_client.on_message = self._on_mqtt_message
        self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
        
        try:
            logger.info(f"Connecting to MQTT broker: {self.config.mqtt_broker}:{self.config.mqtt_port}")
            self.mqtt_client.connect(
                self.config.mqtt_broker,
                self.config.mqtt_port,
                keepalive=60
            )
        except Exception as e:
            logger.error(f"Failed to connect to MQTT: {e}")
            raise
    
    # ========================================================================
    # MQTT CALLBACKS
    # ========================================================================
    
    def _on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("✓ Connected to MQTT broker")
            client.subscribe(self.config.input_topic)
            logger.info(f"✓ Subscribed to topic: {self.config.input_topic}")
        else:
            logger.error(f"✗ MQTT connection failed with code {rc}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc):
        logger.warning(f"Disconnected from MQTT broker (code: {rc})")
        if self.running:
            logger.info("Attempting to reconnect...")
    
    def _on_mqtt_message(self, client, userdata, message):
        """MQTT message callback - Forward all data to cloud"""
        try:
            payload = json.loads(message.payload.decode())
            device_id = payload.get("device_id")
            
            # Filter: only process messages from managed devices
            if device_id not in self.config.managed_devices:
                logger.debug(f"Ignoring message from unmanaged device: {device_id}")
                return
            
            logger.debug(f"Received data from {device_id}")
            
            # Step 1: Store raw reading in Redis (for reference)
            self.redis_manager.store_reading(device_id, payload, ttl=86400)
            logger.debug(f"[{device_id}] Raw reading stored in Redis")
            
            # Step 2: Forward directly to Cloud (no anomaly detection here)
            self._forward_to_cloud(device_id, payload)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode MQTT message: {e}")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    # ========================================================================
    # CLOUD FORWARDING
    # ========================================================================
    
    def _forward_to_cloud(self, device_id: str, reading: dict) -> None:
        """
        Forward sensor reading to Cloud Layer
        
        Args:
            device_id: Device identifier
            reading: Raw sensor data
        """
        try:
            payload = {
                "edge_node": self.node_id,
                "device_id": device_id,
                "timestamp": time.time(),
                **reading  # Include all sensor data
            }
            
            # Publish to cloud topic
            self.mqtt_client.publish(
                self.config.cloud_topic,
                json.dumps(payload),
                qos=1
            )
            
            logger.info(f"✓ Forwarded data to cloud: {device_id}")
            
        except Exception as e:
            logger.error(f"Failed to forward to cloud: {e}")
    
    # ========================================================================
    # LIFECYCLE
    # ========================================================================
    
    def start(self) -> None:
        """Start edge node"""
        self.running = True
        logger.info(f"Starting {self.node_id}...")
        
        self.mqtt_client.loop_start()
        
        try:
            while self.running:
                time.sleep(30)
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
            self.stop()
    
    def stop(self) -> None:
        """Stop edge node gracefully"""
        logger.info(f"Stopping {self.node_id}...")
        self.running = False
        
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        if self.redis_manager:
            self.redis_manager.redis_client.close()
        
        logger.info(f"{self.node_id} stopped")

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    import os
    
    node_id = os.environ.get("EDGE_NODE_ID", "edge-europe")
    logger.info(f"Starting Edge Node: {node_id}")
    
    try:
        edge_node = EdgeNode(node_id)
        
        def signal_handler(sig, frame):
            logger.info("Received shutdown signal")
            edge_node.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        edge_node.start()
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
