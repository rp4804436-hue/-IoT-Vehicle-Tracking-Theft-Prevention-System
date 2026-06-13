/**
 * @file esp32_tracker.ino
 * @brief Production-grade firmware for IoT Vehicle Tracking Edge Node.
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <TinyGPS++.h>

// Network Identity Configuration
const char* WIFI_SSID         = "YOUR_WIFI_SSID";
const char* WIFI_PASSWORD     = "YOUR_WIFI_PASSWORD";
const char* MQTT_BROKER_HOST  = "broker.hivemq.com";
const int   MQTT_BROKER_PORT  = 1883;

// Application Topic Declarations
const char* TOPIC_TELEMETRY   = "vehicle/telemetry";
const char* TOPIC_COMMANDS    = "vehicle/commands";

// Hardware Pin Layout Declaration
#define PIN_GPS_RX       16
#define PIN_GPS_TX       17
#define PIN_RELAY_KILL   25
#define PIN_ALERT_BUZZER 26
#define PIN_STATUS_LED   2

// Object Instantiations
WiFiClient espNetworkClient;
PubSubClient mqttClient(espNetworkClient);
TinyGPSPlus gpsParser;
HardwareSerial serialGPS(2); 

// System State Machine Variables
bool isVehicleLocked = false;
unsigned long lastTelemetryTimestamp = 0;
const unsigned long TELEMETRY_INTERVAL_MS = 5000;

void setup() {
    Serial.begin(115200);
    
    pinMode(PIN_RELAY_KILL, OUTPUT);
    pinMode(PIN_ALERT_BUZZER, OUTPUT);
    pinMode(PIN_STATUS_LED, OUTPUT);
    
    // Default safe state: Engine connected, alarms silent
    digitalWrite(PIN_RELAY_KILL, HIGH); 
    digitalWrite(PIN_ALERT_BUZZER, LOW);
    digitalWrite(PIN_STATUS_LED, LOW);

    serialGPS.begin(9600, SERIAL_8N1, PIN_GPS_RX, PIN_GPS_TX);
    
    Serial.printf("[NET] Associating with Wi-Fi: %s\n", WIFI_SSID);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.printf("\n[NET] Connected. IP Address: %s\n", WiFi.localIP().toString().c_str());

    mqttClient.setServer(MQTT_BROKER_HOST, MQTT_BROKER_PORT);
    mqttClient.setCallback(processIncomingMQTTMessage);
}

void loop() {
    if (!mqttClient.connected()) {
        while (!mqttClient.connected()) {
            String clientIdentifier = "ESP32-TrackerClient-" + String(random(0xffff), HEX);
            if (mqttClient.connect(clientIdentifier.c_str())) {
                mqttClient.subscribe(TOPIC_COMMANDS);
            } else {
                delay(5000);
            }
        }
    }
    mqttClient.loop();

    while (serialGPS.available() > 0) {
        gpsParser.encode(serialGPS.read());
    }

    if (millis() - lastTelemetryTimestamp >= TELEMETRY_INTERVAL_MS) {
        char jsonPayloadBuffer[256];
        double currentLatitude = gpsParser.location.isValid() ? gpsParser.location.lat() : 28.6139; 
        double currentLongitude = gpsParser.location.isValid() ? gpsParser.location.lng() : 77.2090;
        double operationalSpeed = gpsParser.speed.kmph();

        snprintf(jsonPayloadBuffer, sizeof(jsonPayloadBuffer),
                 "{\"latitude\":%.6f,\"longitude\":%.6f,\"speed\":%.2f,\"locked\":%s}",
                 currentLatitude, currentLongitude, operationalSpeed, isVehicleLocked ? "true" : "false");

        mqttClient.publish(TOPIC_TELEMETRY, jsonPayloadBuffer);
        lastTelemetryTimestamp = millis();
    }
}

void processIncomingMQTTMessage(char* topic, byte* payload, unsigned int length) {
    String commandPayload = "";
    for (unsigned int i = 0; i < length; i++) {
        commandPayload += (char)payload[i];
    }

    if (commandPayload.equalsIgnoreCase("LOCK")) {
        isVehicleLocked = true;
        digitalWrite(PIN_RELAY_KILL, LOW); // Cut car ignition circuit
        digitalWrite(PIN_STATUS_LED, HIGH);
    } 
    else if (commandPayload.equalsIgnoreCase("UNLOCK")) {
        isVehicleLocked = false;
        digitalWrite(PIN_RELAY_KILL, HIGH); // Restore ignition circuit
        digitalWrite(PIN_STATUS_LED, LOW);
        digitalWrite(PIN_ALERT_BUZZER, LOW); 
    }
}