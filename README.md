# IoT Vehicle Tracking & Theft Prevention System

## 📌 Project Overview
This repository contains a full-stack, production-grade IoT asset telematics and active theft mitigation framework. The project is uniquely engineered with a dual-paradigm execution architecture: it can be deployed directly to physical hardware (ESP32 Edge Node) or run as a completely zero-hardware virtual desktop simulation environment. This hybrid flexibility makes it an exceptional open-source asset for engineering course demonstrations, portfolio reviews, and technical placement interviews.

## ⚠️ The Problem Statement
Commercial fleet assets and personal vehicles remain highly vulnerable to vehicle theft, route non-compliance, towing events, and unauthorized perimeter border crossings. Traditional vehicle tracking units fail to actively mitigate threats, operating strictly as passive loggers that are easily disabled by on-site intruders. 

This project addresses these security flaws by engineering an active, zero-trust edge-to-cloud security grid capable of real-time monitoring, autonomous geofence threshold enforcement, and instant remote engine immobilization.

## 🏗 System Architecture & Processing Workflow
1. **Edge Telemetry Acquisition:** The NEO-6M GPS module streams precise raw satellite NMEA-0183 sentences via a hardware serial UART link.
2. **Parsing & Transit Framework:** The central ESP32 processor decodes raw coordinates, encapsulates the telematics into a structured JSON payload, and publishes it down `vehicle/telemetry` over a lightweight MQTT protocol.
3. **Analytical Processing Core:** A Python central application engine captures the live MQTT message queue and continually evaluates the great-circle displacement distance utilizing the mathematical **Haversine Formula**:

$$d = 2R \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta\lambda}{2}\right)}\right)$$

4. **Active Threat Mitigation:** If tracking coordinates cross the predefined safe geofence radius ($150\text{ meters}$) while the ignition lock state is armed, the system triggers local acoustic sirens, activates a physical engine cut-off relay, flashes critical dashboard alerts, and updates a local append-only logging database.
