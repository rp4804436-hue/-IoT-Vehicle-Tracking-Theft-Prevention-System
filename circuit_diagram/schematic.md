# Hardware Interconnection Ledger

| Source Component | Source Pin | Destination Component | Destination Pin | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| NEO-6M GPS | VCC | ESP32 | 3V3 | Power allocation |
| NEO-6M GPS | GND | ESP32 | GND | Shared reference ground plane |
| NEO-6M GPS | TX | ESP32 | GPIO 16 (RX2) | Hardware serial telemetry data data stream |
| NEO-6M GPS | RX | ESP32 | GPIO 17 (TX2) | Configuration logic commands |
| 5V Relay Module | VCC | ESP32 | VIN (5V) | Relay magnetic coil activation power |
| 5V Relay Module | GND | ESP32 | GND | Shared reference ground plane |
| 5V Relay Module | IN / Signal | ESP32 | GPIO 25 | Active low engine kill logic |
| Active Buzzer | Positive (+) | ESP32 | GPIO 26 | Alarm output activation trigger |
| Active Buzzer | Negative (-) | ESP32 | GND | Shared reference ground plane |
| Diagnostic LED | Anode (+) | ESP32 | GPIO 2 | Local status warning indicator |