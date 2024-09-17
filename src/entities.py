import math
import logging
from calculations import geodetic_to_ecef, ecef_to_geodetic
from events import MovementEvent  # Import needed event classes

# Create a logger for entities
entity_logger = logging.getLogger('entity')

# Define a small tolerance to avoid precision errors when checking ground impact
GROUND_TOLERANCE = 1.0  # Increased tolerance for ground impact detection to 1 meter

class Entity:
    def __init__(self, lat, lon, alt, velocity, orientation, entity_id=None, max_velocity=300):
        self.lat = lat  # Latitude
        self.lon = lon  # Longitude
        self.alt = alt  # Altitude
        self.velocity = velocity  # Velocity vector [vx, vy, vz]
        self.orientation = orientation  # Orientation [pitch, yaw, roll]
        self.entity_id = entity_id if entity_id else self.generate_unique_id()
        self.max_velocity = max_velocity  # Maximum velocity in powered flight

        # Initialize ECEF coordinates using geodetic to ECEF conversion
        self.X, self.Y, self.Z = geodetic_to_ecef(self.lat, self.lon, self.alt)

    def move(self, time_step, env):
        """Update entity position based on its velocity."""
        # Update ECEF position
        self.X += self.velocity[0] * time_step
        self.Y += self.velocity[1] * time_step
        self.Z += self.velocity[2] * time_step

        # Convert ECEF back to geodetic for logging
        self.lat, self.lon, self.alt = ecef_to_geodetic(self.X, self.Y, self.Z)

        # Log the new position
        self._log_position()

    def _log_position(self):
        """Log the entity's current position and orientation."""
        entity_logger.info(f"Entity {self.entity_id} moved to ECEF ({self.X}, {self.Y}, {self.Z})")
        entity_logger.info(f"Entity {self.entity_id} moved to lat: {self.lat}, lon: {self.lon}, alt: {self.alt}")
        entity_logger.info(f"Entity {self.entity_id} orientation: pitch: {self.orientation[0]}, yaw: {self.orientation[1]}, roll: {self.orientation[2]}")

    def _has_hit_ground(self):
        """Check if the entity has hit the ground."""
        _, _, alt = ecef_to_geodetic(self.X, self.Y, self.Z)
        return alt <= GROUND_TOLERANCE

    def _handle_ground_impact(self):
        """Handle what happens when the entity hits the ground."""
        self.Z = 0  # Ensure it stays on the ground
        self.has_hit_ground = True
        entity_logger.info(f"Entity {self.entity_id} hit the ground.")

    def schedule_event(self, event_type, env, time_step):
        """Schedule the next event."""
        next_event_time = env.current_time + time_step
        env.schedule_event(event_type(next_event_time, self, time_step))

    def handle_event(self, event, env):
        """Handle events like movement."""
        if isinstance(event, MovementEvent):
            self.move(event.time_step, env)

class Aircraft(Entity):

    def __init__(self, lat, lon, alt, velocity, orientation, entity_id=None):
        super().__init__(lat, lon, alt, velocity, orientation, entity_id)

    def move(self, time_step, env):
        """Handle aircraft-specific movement logic."""
        super().move(time_step, env)
        self.update_orientation(pitch_change=2 * time_step, yaw_change=3 * time_step)

class Ship(Entity):
    def __init__(self, lat, lon, alt, velocity, orientation, entity_id=None):
        super().__init__(lat, lon, alt, velocity, orientation, entity_id)

    def launch(self, target, env):
        """Ship launching a missile."""
        entity_logger.info(f"Ship {self.entity_id} launched a missile at {target.entity_id}")