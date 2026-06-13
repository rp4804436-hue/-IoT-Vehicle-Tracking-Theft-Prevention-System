#!/usr/bin/env python3
"""
main.py
Master execution orchestration file for the Vehicle Security System.
"""

import sys
import json
import tkinter as tk
import paho.mqtt.client as mqtt
from dashboard.gui_app import TrackingDashboard

MQTT_HOST = "broker.hivemq.com"
MQTT_PORT = 1883

class CoreApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("System Live Control Console")
        self.root.geometry("820x520")
        self.root.configure(bg="#1E1E24")

        # Instantiate visualization dashboard frame layout
        self.view = TrackingDashboard(self.root, None)

        # Initialize network gateway client variables
        self.client = mqtt.Client()
        self.client.on_message = self._on_message_received
        
        # Link initialized client back to view dashboard action components
        self.view.mqtt_client = self.client

        self._connect_network_gateway()

    def _connect_network_gateway(self):
        try:
            self.client.connect(MQTT_HOST, MQTT_PORT, 60)
            self.client.subscribe("vehicle/telemetry")
            self.client.loop_start()
            print("[NET] Connected to MQTT broker infrastructure successfully.")
        except Exception as e:
            print(f"[NET ERROR] Gateway connection initialization failure: {e}")

    def _on_message_received(self, client, userdata, msg):
        if msg.topic == "vehicle/telemetry":
            try:
                data = json.loads(msg.payload.decode())
                # Safely schedule GUI frame updates on the main execution thread
                self.root.after(0, self.view.update_telemetry_display, data)
            except Exception as err:
                print(f"[DATA ERROR] Drop message sequence matching illegal JSON shape: {err}")

    def run(self):
        try:
            self.root.mainloop()
        finally:
            self.client.loop_stop()

if __name__ == "__main__":
    app = CoreApplication()
    app.run()