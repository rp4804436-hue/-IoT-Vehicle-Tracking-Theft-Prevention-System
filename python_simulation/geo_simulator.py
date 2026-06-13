"""
geo_simulator.py
Provides a virtual simulation engine to broadcast mock GPS data strings.
"""

import json

class VehicleSimulator:
    @staticmethod
    def get_scenario_payload(scenario_id, system_lock_state):
        """Generates mock telemetry data matching specific tracking scenarios."""
        # Baseline Safe Zone Center Coordinate Constants
        base_lat = 28.6139
        base_lon = 77.2090
        
        is_locked_bool = True if system_lock_state == "LOCK" else False

        if scenario_id == 1:
            # Scenario 1: Normal Parked Baseline Operations
            return json.dumps({"latitude": base_lat, "longitude": base_lon, "speed": 0.0, "locked": is_locked_bool})
        elif scenario_id == 2:
            # Scenario 2: Active Authorized Cruise Operations
            return json.dumps({"latitude": 28.6145, "longitude": 77.2110, "speed": 42.5, "locked": is_locked_bool})
        elif scenario_id == 3:
            # Scenario 3: Geofence Arc Displacement Breach
            return json.dumps({"latitude": 28.6165, "longitude": 77.2199, "speed": 58.0, "locked": is_locked_bool})
        elif scenario_id == 4:
            # Scenario 4: Parked Theft Event Bypass
            return json.dumps({"latitude": 28.6195, "longitude": 77.2265, "speed": 35.2, "locked": True})
        else:
            return json.dumps({"latitude": base_lat, "longitude": base_lon, "speed": 0.0, "locked": is_locked_bool})