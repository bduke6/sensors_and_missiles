import math
import logging
from calculations import geodetic_to_ecef, ecef_to_geodetic
from events import MovementEvent  # Import needed event classes

# Create a logger for entities
entity_logger = logging.getLogger('entity')

# Define a small tolerance to avoid precision errors when checking ground impact
GROUND_TOLERANCE = 1.0  # Increased tolerance for ground impact detection to 1 meter

class Entity:
    def __init__(self, lat, lon, alt, velocity, orientation, entity_id=None):
        self.lat = lat  # Latitude
        self.lon = lon  # Longitude
        self.alt = alt  # Altitude
        self.velocity = velocity  # Velocity vector [vx, vy, vz]
        self.orientation = orientation  # Orientation [pitch, yaw, roll]
        self.entity_id = entity_id if entity_id else self.generate_unique_id()

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



class Missile(Entity):
            

    def __init__(self, lat, lon, alt, velocity, orientation, entity_id=None, fuel=100):
        super().__init__(lat, lon, alt, velocity, orientation, entity_id)
        self.fuel = fuel
        self.acceleration = [0, 0, 0]  # Acceleration along [x, y, z]
        self.gravity = 9.81  # Gravity value for downward acceleration

    def launch(self, target, env):
        """Initiate missile launch."""
        entity_logger.info(f"Missile {self.entity_id} launched at target {target.entity_id}")

        # Set initial speed and calculate components based on orientation (pitch and yaw)
        initial_speed = 300.0  # Speed during launch (adjust as needed)
        pitch_radians = math.radians(self.orientation[0])
        yaw_radians = math.radians(self.orientation[1])

        # Decompose initial speed into vertical (Z) and horizontal (X, Y) components
        horizontal_speed = initial_speed * math.cos(pitch_radians)
        self.velocity[2] = initial_speed * math.sin(pitch_radians)
        self.velocity[0] = horizontal_speed * math.cos(yaw_radians)
        self.velocity[1] = horizontal_speed * math.sin(yaw_radians)
        self.acceleration[2] = 15.0  # Example upward acceleration to counteract gravity and provide thrust

        entity_logger.info(f"Missile {self.entity_id} initial velocity: {self.velocity}")
        self.schedule_event(MovementEvent, env, time_step=1)

    def move(self, time_step, env):
        """Handle missile movement, accounting for fuel, thrust, and gravity."""
        print(f"########## MISSILE ALTIDUE: {self.alt}")
        print(f"MISSILE MISSILE MISSILE{self.entity_id} moving with fuel: {self.fuel}")
        if self.fuel > 0:
            self._apply_thrust(time_step)
        else:
            self._glide_with_gravity(time_step)

        super().move(time_step, env)

        if not self._has_hit_ground():
            self.schedule_event(MovementEvent, env, time_step=1)

    def _apply_thrust(self, time_step):
        """Apply thrust while fuel is available."""
        entity_logger.info(f"Missile {self.entity_id} is in powered flight.")
        self.velocity[2] += (self.acceleration[2] - self.gravity) * time_step
        self.velocity[0] += self.acceleration[0] * time_step
        self.velocity[1] += self.acceleration[1] * time_step
        entity_logger.info(f"Missile {self.entity_id} velocity: {self.velocity}")
        self.fuel -= time_step * 10
        if self.fuel <= 0:
            self._switch_to_glide()

    def _switch_to_glide(self):
        """Switch to glide mode when fuel runs out."""
        self.acceleration = [0, 0, -self.gravity]
        entity_logger.info(f"Missile {self.entity_id} ran out of fuel. Switching to glide.")

    def _glide_with_gravity(self, time_step):
        """Apply gravity to vertical velocity while gliding horizontally."""
        entity_logger.info(f"Missile {self.entity_id} is in no_power (glide) flight.")
        self.velocity[2] += self.acceleration[2] * time_step  # Apply gravity (downward)

        # Ensure the horizontal velocity remains steady and does not drop to near-zero
        horizontal_speed = max((self.velocity[0] ** 2 + self.velocity[1] ** 2) ** 0.5, 1.0)  # Cap minimal horizontal speed
        self.velocity[0] = horizontal_speed * math.cos(math.radians(self.orientation[1]))
        self.velocity[1] = horizontal_speed * math.sin(math.radians(self.orientation[1]))

        entity_logger.info(f"Missile {self.entity_id} gliding with velocity: {self.velocity}")

        self._update_orientation_based_on_velocity()
        self._log_position()



    def _update_orientation_based_on_velocity(self):

        # Constants to define the maximum allowable changes in orientation per time step
        MAX_PITCH_CHANGE = 10  # Maximum change in pitch (degrees) per time step
        MAX_YAW_CHANGE = 5     # Maximum change in yaw (degrees) per time step
        MAX_ROLL_CHANGE = 5    # Maximum change in roll (degrees) per time step
        """Update the missile's orientation based on its current velocity vector."""
        vertical_speed = self.velocity[2]
        horizontal_speed = max((self.velocity[0] ** 2 + self.velocity[1] ** 2) ** 0.5, 1.0)  # Avoid division by zero

        # Calculate the target pitch based on the current velocity vector
        target_pitch = math.degrees(math.atan2(vertical_speed, horizontal_speed))
        
        # Smoothly transition to the target pitch, with a max pitch change limit
        self.orientation[0] = self._apply_max_orientation_change(self.orientation[0], target_pitch, MAX_PITCH_CHANGE)

        # You can similarly update yaw and roll based on other factors if needed
        # For example, yaw might depend on lateral movement, and roll could depend on specific maneuvering rules
        # In this case, we'll leave yaw and roll unchanged unless needed, but the same logic can apply.
        # Example (if yaw/roll were updated): 
        # self.orientation[1] = self._apply_max_orientation_change(self.orientation[1], target_yaw, MAX_YAW_CHANGE)
        # self.orientation[2] = self._apply_max_orientation_change(self.orientation[2], target_roll, MAX_ROLL_CHANGE)

        entity_logger.info(f"Missile {self.entity_id} orientation updated: pitch: {self.orientation[0]}, yaw: {self.orientation[1]}, roll: {self.orientation[2]}")

    def _apply_max_orientation_change(self, current_value, target_value, max_change):
        """Limit the change in orientation to the specified maximum."""
        # Calculate the difference between the target and current values
        delta = target_value - current_value

        # Limit the change to the maximum allowable value
        if abs(delta) > max_change:
            delta = max_change if delta > 0 else -max_change

        # Apply the limited change and return the updated orientation value
        return current_value + delta

    def _log_position(self):
        """Log the missile's position and orientation."""
        entity_logger.info(f"Entity {self.entity_id} moved to lat: {self.lat}, lon: {self.lon}, alt: {self.alt}")
        entity_logger.info(f"Entity {self.entity_id} orientation: pitch: {self.orientation[0]}, yaw: {self.orientation[1]}, roll: {self.orientation[2]}")


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