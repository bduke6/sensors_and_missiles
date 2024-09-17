import math
import logging
from calculations import geodetic_to_ecef, ecef_to_geodetic, calculate_distance_and_bearing
from events import MovementEvent  # Import needed event classes

# Create a logger for the missile
missile_logger = logging.getLogger('missile')

# Constants
APOGEE_ALTITUDE = 80000  # Example apogee altitude for DF-21D in meters
GROUND_TOLERANCE = 1.0  # Increased tolerance for ground impact detection to 1 meter

class Missile:
    def __init__(self, lat, lon, alt, velocity, orientation, entity_id=None, fuel=100, max_velocity=300):
        self.lat = lat  # Latitude
        self.lon = lon  # Longitude
        self.alt = alt  # Altitude
        self.velocity = velocity  # Velocity vector [vx, vy, vz]
        self.orientation = orientation  # Orientation [pitch, yaw, roll]
        self.entity_id = entity_id if entity_id else self.generate_unique_id()
        self.max_velocity = max_velocity
        self.fuel = fuel
        self.acceleration_rate = 10  # Acceleration per second during powered flight
        self.deceleration_rate = 5   # Deceleration rate in no-power flight
        self.gravity = 9.81  # Gravity value for downward acceleration
        self.apogee_reached = False
        self.target = None  # To store the target's coordinates

        # Initialize ECEF coordinates using geodetic to ECEF conversion
        self.X, self.Y, self.Z = geodetic_to_ecef(self.lat, self.lon, self.alt)

    def launch(self, target, env):
        """Initiate missile launch."""
        self.target = target
        missile_logger.info(f"Missile {self.entity_id} launched at target {target.entity_id}")

        # Set initial speed and calculate components based on orientation (pitch and yaw)
        initial_speed = 300.0  # Speed during launch (adjust as needed)
        pitch_radians = math.radians(self.orientation[0])
        yaw_radians = math.radians(self.orientation[1])

        # Decompose initial speed into vertical (Z) and horizontal (X, Y) components
        horizontal_speed = initial_speed * math.cos(pitch_radians)
        self.velocity[2] = initial_speed * math.sin(pitch_radians)
        self.velocity[0] = horizontal_speed * math.cos(yaw_radians)
        self.velocity[1] = horizontal_speed * math.sin(yaw_radians)

        missile_logger.info(f"Missile {self.entity_id} initial velocity: {self.velocity}")
        self.schedule_event(MovementEvent, env, time_step=1)

    def move(self, time_step, env):
        """Handle missile movement, accounting for fuel, thrust, and gravity."""
        if self.fuel > 0:
            self._apply_thrust(time_step)
        elif self.alt >= APOGEE_ALTITUDE and not self.apogee_reached:
            self._switch_to_glide()
        elif self.apogee_reached:
            self._glide_with_gravity(time_step)

        self._update_position(time_step, env)

        if not self._has_hit_ground():
            self.schedule_event(MovementEvent, env, time_step=1)

    def _apply_thrust(self, time_step):
        """Apply thrust while fuel is available."""
        missile_logger.info(f"Missile {self.entity_id} is in powered flight.")
        if self.alt >= APOGEE_ALTITUDE:
            missile_logger.info(f"Missile {self.entity_id} reached apogee at {self.alt} meters.")
            self.apogee_reached = True
            self._switch_to_glide()

        self.velocity[2] += (self.acceleration_rate - self.gravity) * time_step
        self.fuel -= time_step * 10  # Decrease fuel

        if self.fuel <= 0:
            self._switch_to_glide()

    def _switch_to_glide(self):
        """Switch to glide mode when apogee is reached or fuel runs out."""
        missile_logger.info(f"Missile {self.entity_id} switching to glide mode.")
        self.acceleration_rate = 0  # No more thrust
        self.deceleration_rate = 5   # Apply deceleration
        self._set_glide_orientation()

    def _glide_with_gravity(self, time_step):
        """Glide towards the target with gravity affecting vertical velocity."""
        missile_logger.info(f"Missile {self.entity_id} is gliding towards the target.")
        
        current_speed = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
        deceleration = self.deceleration_rate * time_step
        new_speed = max(current_speed - deceleration, 0)
        scale_factor = new_speed / current_speed if current_speed != 0 else 1.0
        self.velocity[0] *= scale_factor
        self.velocity[1] *= scale_factor
        self.velocity[2] -= self.gravity * time_step

        missile_logger.info(f"Missile {self.entity_id} velocity during glide: {self.velocity}")
        self._log_position()

    def _set_glide_orientation(self):
        """Adjust missile orientation to glide towards the target."""
        distance, bearing = calculate_distance_and_bearing(self.lat, self.lon, self.target.lat, self.target.lon)
        self.orientation[1] = bearing
        self.orientation[0] = -45  # Set descent pitch
        missile_logger.info(f"Missile {self.entity_id} adjusted orientation for glide: pitch {self.orientation[0]}, yaw {self.orientation[1]}")

    def _update_position(self, time_step, env):
        """Update the missile position based on its velocity."""
        self.X += self.velocity[0] * time_step
        self.Y += self.velocity[1] * time_step
        self.Z += self.velocity[2] * time_step
        self.lat, self.lon, self.alt = ecef_to_geodetic(self.X, self.Y, self.Z)
        self._log_position()

    def _log_position(self):
        """Log the missile's current position and orientation."""
        missile_logger.info(f"Missile {self.entity_id} moved to ECEF ({self.X}, {self.Y}, {self.Z})")
        missile_logger.info(f"Missile {self.entity_id} moved to lat: {self.lat}, lon: {self.lon}, alt: {self.alt}")
        missile_logger.info(f"Missile {self.entity_id} orientation: pitch: {self.orientation[0]}, yaw: {self.orientation[1]}, roll: {self.orientation[2]}")

    def _has_hit_ground(self):
        """Check if the missile has hit the ground."""
        _, _, alt = ecef_to_geodetic(self.X, self.Y, self.Z)
        return alt <= GROUND_TOLERANCE

    def schedule_event(self, event_type, env, time_step):
        """Schedule the next event."""
        next_event_time = env.current_time + time_step
        env.schedule_event(event_type(next_event_time, self, time_step))

    def handle_event(self, event, env):
        """Handle events like movement."""
        if isinstance(event, MovementEvent):
            self.move(event.time_step, env)
        # Handle other events here as necessary