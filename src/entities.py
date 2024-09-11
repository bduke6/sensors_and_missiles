import uuid
from calculations import geodetic_to_ecef, ecef_to_geodetic
import logging
from events import MovementEvent  # Import needed event classes
import math

# Create a logger for entities
entity_logger = logging.getLogger('entity')

# Define a small tolerance to avoid precision errors when checking ground impact
GROUND_TOLERANCE = 0.01  # 1 cm tolerance for hitting the ground

class Entity:
    def __init__(self, lat, lon, alt, velocity, orientation, entity_id=None):
        # Convert geodetic to ECEF
        self.X, self.Y, self.Z = geodetic_to_ecef(lat, lon, alt)
        self.velocity = velocity  # Should be [vx, vy, vz] for movement in ECEF
        self.orientation = orientation  # Orientation as [pitch, yaw, roll]
        self.entity_id = entity_id or str(uuid.uuid4())
        self.has_hit_ground = False

    def move(self, time_step, env):
        """Update position and handle movement."""
        self._update_position(time_step)
        self._log_position()

        if self._has_hit_ground():
            self._handle_ground_impact()
        else:
            self.schedule_event(MovementEvent, env, time_step)

    def _update_position(self, time_step):
        """Update the ECEF position based on velocity and time."""
        self.X += self.velocity[0] * time_step
        self.Y += self.velocity[1] * time_step
        self.Z += self.velocity[2] * time_step

    def _log_position(self):
        """Log the current position and orientation."""
        lat, lon, alt = ecef_to_geodetic(self.X, self.Y, self.Z)
        entity_logger.info(f"Entity {self.entity_id} moved to ECEF ({self.X}, {self.Y}, {self.Z})")
        entity_logger.info(f"Entity {self.entity_id} moved to lat: {lat}, lon: {lon}, alt: {alt}")
        entity_logger.info(f"Entity {self.entity_id} orientation: "
                           f"pitch: {self.orientation[0]}, yaw: {self.orientation[1]}, roll: {self.orientation[2]}")

    def _has_hit_ground(self):
        """Check if the entity has hit the ground."""
        _, _, alt = ecef_to_geodetic(self.X, self.Y, self.Z)
        return alt <= GROUND_TOLERANCE

    def _handle_ground_impact(self):
        """Handle what happens when the entity hits the ground."""
        self.Z = 0  # Ensure it stays on the ground
        self.has_hit_ground = True
        entity_logger.info(f"Entity {self.entity_id} hit the ground.")

    def update_orientation(self, pitch_change=0, yaw_change=0, roll_change=0):
        """Update orientation and ensure it stays within bounds."""
        self.orientation = [(angle + change) % 360 
                            for angle, change in zip(self.orientation, [pitch_change, yaw_change, roll_change])]
        entity_logger.info(f"Entity {self.entity_id} orientation updated to pitch: {self.orientation[0]}, "
                           f"yaw: {self.orientation[1]}, roll: {self.orientation[2]}")

    def handle_event(self, event, env):
        """Handle events like movement."""
        if isinstance(event, MovementEvent):
            self.move(event.time_step, env)

    def schedule_event(self, event_type, env, time_step):
        """Schedule the next event."""
        next_event_time = env.current_time + time_step
        env.schedule_event(event_type(next_event_time, self, time_step))


class Ship(Entity):
    def __init__(self, lat, lon, alt, velocity, orientation, entity_id=None):
        super().__init__(lat, lon, alt, velocity, orientation, entity_id)

    def launch(self, target, env):
        """Ship launching a missile."""
        entity_logger.info(f"Ship {self.entity_id} launched a missile at {target.entity_id}")


class Missile(Entity):
    def __init__(self, lat, lon, alt, velocity, orientation, entity_id=None, fuel=100):
        super().__init__(lat, lon, alt, velocity, orientation, entity_id)
        self.fuel = fuel
        self.acceleration = [0, 0, 0]  # Acceleration along [x, y, z]

    def launch(self, target, env):
        """Initiate missile launch."""
        entity_logger.info(f"Missile {self.entity_id} launched at target {target.entity_id}")
        self.acceleration = [0, 0, 9.81]  # Initial upward acceleration (if applicable)
        self.schedule_event(MovementEvent, env, time_step=0.1)

    def move(self, time_step, env):
        """Handle missile movement, accounting for fuel, thrust, gravity, and glide."""
        if self.fuel > 0:
            self._apply_thrust(time_step)
        else:
            self._glide_with_gravity(time_step)  # Apply glide and gravity

        super().move(time_step, env)

    def _apply_thrust(self, time_step):
        """Apply thrust while fuel is available."""
        for i in range(3):
            self.velocity[i] += self.acceleration[i] * time_step
        entity_logger.info(f"Missile {self.entity_id} velocity: {self.velocity}")
        self.fuel -= time_step * 10
        entity_logger.info(f"Missile {self.entity_id} fuel remaining: {self.fuel}")
        if self.fuel <= 0:
            self._switch_to_glide()

    def _switch_to_glide(self):
        """Switch to glide mode when fuel runs out."""
        self.acceleration = [0, 0, -9.81]  # Apply only gravity in the Z direction
        entity_logger.info(f"Missile {self.entity_id} ran out of fuel. Switching to glide.")

    def _glide_with_gravity(self, time_step):
        """Apply gravity to vertical velocity while gliding horizontally."""
        # Gravity only affects the Z-axis (vertical movement)
        self.velocity[2] += self.acceleration[2] * time_step  # Gravity on Z-axis
        
        # Horizontal velocity (X and Y) remains constant, so no change to X and Y velocity
        entity_logger.info(f"Missile {self.entity_id} gliding with velocity: {self.velocity}")
        
        # Update orientation based on the velocity vector instead of forcing to 270°
        self._update_orientation_based_on_velocity()

    def _update_orientation_based_on_velocity(self):
        """Update the missile's orientation based on its current velocity vector."""
        # Calculate the new pitch based on the vertical and horizontal components of velocity
        vertical_speed = self.velocity[2]
        horizontal_speed = (self.velocity[0] ** 2 + self.velocity[1] ** 2) ** 0.5

        # New pitch: arctan(vertical_speed / horizontal_speed) converted to degrees
        # atan2 accounts for direction and quadrant of the vector
        new_pitch = math.degrees(math.atan2(vertical_speed, horizontal_speed))

        # Update pitch while keeping yaw and roll the same
        self.orientation[0] = new_pitch

        # Log the orientation after the update
        entity_logger.info(f"Missile {self.entity_id} orientation based on velocity: "
                           f"pitch: {self.orientation[0]}, yaw: {self.orientation[1]}, roll: {self.orientation[2]}")


class Aircraft(Entity):
    def __init__(self, lat, lon, alt, velocity, orientation, entity_id=None):
        super().__init__(lat, lon, alt, velocity, orientation, entity_id)

    def move(self, time_step, env):
        """Handle aircraft-specific movement logic."""
        super().move(time_step, env)
        self.update_orientation(pitch_change=2 * time_step, yaw_change=3 * time_step)
