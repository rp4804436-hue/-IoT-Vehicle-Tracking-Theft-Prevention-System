# System Architecture Specification

## 1. Edge Layer (ESP32)
* Operates asynchronously using an event loop to monitor incoming UART data streams from the NEO-6M.
* Decodes NMEA-0183 payloads via the `TinyGPS++` object model.
* Publishes high-frequency JSON arrays down `vehicle/telemetry` over persistent TCP/IP pipes.

## 2. Transport Layer (MQTT)
* Uses a publish-subscribe broker architecture over HiveMQ infrastructure.
* Decouples real-time embedded tracking hardware from backend tracking dashboards.

## 3. Analytics & Visualization Engine (Python)
* Evaluates geofencing limits using the Haversine trigonometric formula.
* Appends incoming streams to historical CSV sheets and converts runtime arrays into formal PDF compliance reports.