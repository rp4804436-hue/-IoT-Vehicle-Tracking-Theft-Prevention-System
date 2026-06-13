"""
gui_app.py
Builds the visual tracking console application interface using Tkinter.
"""

import os
import csv
import json
import math
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from fpdf import FPDF
from python_simulation.geo_simulator import VehicleSimulator

SAFE_ZONE_LAT = 28.6139
SAFE_ZONE_LON = 77.2090
GEOFENCE_LIMIT_METERS = 150.0
DATA_LOG_PATH = "data/tracking_logs.csv"
PDF_REPORT_PATH = "outputs/safety_report.pdf"

class TrackingDashboard(tk.Frame):
    def __init__(self, master, mqtt_client_ref):
        super().__init__(master)
        self.master = master
        self.mqtt_client = mqtt_client_ref
        self.system_lock_state = "UNLOCKED"
        self.configure(bg="#1E1E24")
        self.pack(fill="both", expand=True)
        self._build_ui()

    def _build_ui(self):
        style = ttk.Style()
        style.configure("TLabel", background="#1E1E24", foreground="#FFF", font=("Courier", 11))

        # Core Telemetry Readouts LabelFrame
        telemetry_frame = tk.LabelFrame(self, text=" Live Tracking Streams ", bg="#1E1E24", fg="#00FF66", font=("Helvetica", 10, "bold"))
        telemetry_frame.pack(fill="x", padx=15, pady=10)

        self.lbl_lat = ttk.Label(telemetry_frame, text="Latitude: --")
        self.lbl_lat.grid(row=0, column=0, padx=25, pady=10)

        self.lbl_lon = ttk.Label(telemetry_frame, text="Longitude: --")
        self.lbl_lon.grid(row=0, column=1, padx=25, pady=10)

        self.lbl_speed = ttk.Label(telemetry_frame, text="Speed: -- km/h")
        self.lbl_speed.grid(row=0, column=2, padx=25, pady=10)

        # High-Visibility System Status Alert Banner
        self.alarm_banner = tk.Label(self, text="SYSTEM INITIALIZED - MONITORING ACTIVE", bg="#004F2D", fg="#00FF66", font=("Helvetica", 12, "bold"))
        self.alarm_banner.pack(fill="x", padx=15, pady=5)

        # Control Operations Action Panel
        control_frame = tk.LabelFrame(self, text=" System Safety Overrides ", bg="#1E1E24", fg="#00FF66", font=("Helvetica", 10, "bold"))
        control_frame.pack(fill="x", padx=15, pady=10)

        tk.Button(control_frame, text="ENGAGE COIL LOCK", bg="#9E2A2B", fg="white", font=("Helvetica", 9, "bold"), width=22, command=lambda: self._send_action("LOCK")).grid(row=0, column=0, padx=20, pady=10)
        tk.Button(control_frame, text="RELEASE COIL LOCK", bg="#3B7A57", fg="white", font=("Helvetica", 9, "bold"), width=22, command=lambda: self._send_action("UNLOCK")).grid(row=0, column=1, padx=20, pady=10)
        tk.Button(control_frame, text="EXPORT COMPLIANCE LOG", bg="#415A77", fg="white", font=("Helvetica", 9, "bold"), width=22, command=self._generate_pdf).grid(row=0, column=2, padx=20, pady=10)

        # Integrated Pure Virtual Simulation Deck
        sim_frame = tk.LabelFrame(self, text=" Hardware-Free Simulation Suite ", bg="#1E1E24", fg="#00FF66", font=("Helvetica", 10, "bold"))
        sim_frame.pack(fill="both", expand=True, padx=15, pady=10)

        tk.Button(sim_frame, text="S1: Stationary Parked", bg="#2A2D34", fg="#FFF", width=24, command=lambda: self._inject_mock(1)).grid(row=0, column=0, padx=15, pady=15)
        tk.Button(sim_frame, text="S2: Authorized Driving", bg="#2A2D34", fg="#FFF", width=24, command=lambda: self._inject_mock(2)).grid(row=0, column=1, padx=15, pady=15)
        tk.Button(sim_frame, text="S3: Geofence Breach", bg="#2A2D34", fg="#FFF", width=24, command=lambda: self._inject_mock(3)).grid(row=0, column=2, padx=15, pady=15)
        tk.Button(sim_frame, text="S4: Critical Theft Event", bg="#D90429", fg="#FFF", width=24, command=lambda: self._inject_mock(4)).grid(row=1, column=1, padx=15, pady=15)

        # Dynamic Map URL Terminal Field
        self.map_txt = tk.Text(self, height=2, bg="#2D2D31", fg="#00E5FF", font=("Courier", 10), borderwidth=0)
        self.map_txt.pack(fill="x", padx=15, pady=10)
        self.map_txt.insert("1.0", "MAP TARGET LINK: Waiting for valid incoming system coordinates...")

    def _send_action(self, state):
        self.system_lock_state = state
        if self.mqtt_client:
            self.mqtt_client.publish("vehicle/commands", state)

    def _inject_mock(self, scenario_id):
        if scenario_id == 4:
            self.system_lock_state = "LOCK"
        payload = VehicleSimulator.get_scenario_payload(scenario_id, self.system_lock_state)
        if self.mqtt_client:
            self.mqtt_client.publish("vehicle/telemetry", payload)

    def update_telemetry_display(self, payload):
        try:
            lat, lon = payload["latitude"], payload["longitude"]
            speed, locked = payload["speed"], payload["locked"]

            self.lbl_lat.config(text=f"Latitude: {lat:.5f}")
            self.lbl_lon.config(text=f"Longitude: {lon:.5f}")
            self.lbl_speed.config(text=f"Speed: {speed:.1f} km/h")

            self.map_txt.delete("1.0", tk.END)
            self.map_txt.insert(tk.END, f"MAP TARGET LINK: https://www.google.com/maps/search/?api=1&query={lat},{lon}")

            # Calculate Haversine great-circle arc displacement
            r = 6371000.0
            p1, p2 = math.radians(lat), math.radians(SAFE_ZONE_LAT)
            dp, dl = math.radians(SAFE_ZONE_LAT - lat), math.radians(SAFE_ZONE_LON - lon)
            a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
            distance = 2 * r * math.atan2(math.sqrt(a), math.sqrt(1-a))

            alert_status = "NONE"
            if distance > GEOFENCE_LIMIT_METERS:
                if locked:
                    self.alarm_banner.config(text=f"⚠️ CRITICAL ALERT: VEHICLE THEFT DETECTED | METERS: {distance:.1f}m", bg="#D90429", fg="#FFF")
                    alert_status = "CRITICAL_THEFT"
                else:
                    self.alarm_banner.config(text=f"⚠️ WARNING: ROUTE GEOFENCE BREACH | METERS: {distance:.1f}m", bg="#F77F00", fg="#FFF")
                    alert_status = "GEOFENCE_BREACH"
            else:
                self.alarm_banner.config(text="SYSTEM SECURE - ACTIVE ANTI-THEFT GUARD LOCK", bg="#004F2D", fg="#00FF66")

            # Write transaction entry append straight to local CSV database
            file_exists = os.path.exists(DATA_LOG_PATH)
            with open(DATA_LOG_PATH, mode="a", newline="") as f:
                w = csv.writer(f)
                if not file_exists:
                    w.writerow(["Timestamp", "Latitude", "Longitude", "Speed", "LockState", "SecurityAlert"])
                w.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), lat, lon, speed, "LOCKED" if locked else "UNLOCKED", alert_status])

        except Exception as e:
            print(f"[ERROR] Failed parsing GUI telemetry string update loop: {e}")

    def _generate_pdf(self):
        if not os.path.exists(DATA_LOG_PATH):
            messagebox.showerror("Error", "No tracking logging files found to compile.")
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(190, 10, "Vehicle Security & Telematics Compliance Audit Log", ln=True, align="C")
        pdf.ln(10)
        
        pdf.set_font("Helvetica", "B", 9)
        headers = ["Timestamp", "Latitude", "Longitude", "Speed", "Lock", "Alert"]
        widths = [45, 28, 28, 20, 25, 44]
        for i, h in enumerate(headers):
            pdf.cell(widths[i], 8, h, 1)
        pdf.ln()

        pdf.set_font("Helvetica", "", 8.5)
        with open(DATA_LOG_PATH, mode="r") as f:
            r = csv.reader(f)
            next(r, None)
            for row in list(r)[-25:]:
                for idx, cell in enumerate(row):
                    pdf.cell(widths[idx], 7, str(cell), 1)
                pdf.ln()

        pdf.output(PDF_REPORT_PATH)
        messagebox.showinfo("Success", f"System safety PDF report written to:\n{PDF_REPORT_PATH}")