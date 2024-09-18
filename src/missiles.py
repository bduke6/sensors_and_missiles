import math
import logging
from calculations import geodetic_to_ecef, ecef_to_geodetic, calculate_distance_and_bearing
from events import MovementEvent  # Import needed event classes

# Create a logger for the missile
missile_logger = logging.getLogger('missile')

# Constants
APOGEE_ALTITUDE = 800000  # Apogee for DF-21D in meters (~800 km)
BOOST_PHASE_DURATION = 120  # Boost phase lasts for 2 minutes (120 seconds)
GROUND_TOLERANCE = 1.0  # Tolerance for ground impact detection
TERMINAL_PHASE_PITCH = -45  # Steep descent in terminal phase
MAX_VELOCITY = 8000  # Updated max velocity during powered flight for realistic speeds (m/s)
GLIDE_DECELERATION_RATE = 1.5  # Updated deceleration rate during glide phase

class Missile:
    def __init__(self, lat, lon, alt, velocity, orientation, entity_id=None, fuel=100, max_velocity=MAX_VELOCITY):
        self.lat = lat  # Latitude
        self.lon = lon  # Longitude
        self.alt = alt  # Altitude
        self.velocity = velocity  # Velocity vector [vx, vy, vz]
        self.orientation = orientation  # Orientation [pitch, yaw, roll]
        self.entity_id = entity_id if entity_id else self.generate_unique_id()
        self.max_velocity = max_velocity  # Maximum velocity in powered flight
        self.fuel = fuel
        self.acceleration_rate = 150  # Updated acceleration rate for boost phase
        self.deceleration_rate = GLIDE_DECELERATION_RATE  # Updated deceleration rate in no-power flight
        self.gravity = 9.81  # Gravity value for downward acceleration
        self.apogee_reached = False
        self.boost_phase = True
        self.target = None  # To store the target's coordinates
        self.elapsed_time = 0  # Track time since launch

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
        """Handle missile movement, accounting for fuel, thrust, gravity, and flight phases."""
        self.elapsed_time += time_step

        # Boost phase (climb to apogee)
        if self.boost_phase and self.elapsed_time <= BOOST_PHASE_DURATION:
            self._apply_thrust(time_step)
            self._adjust_pitch_for_boost_phase()
        elif not self.apogee_reached and self.alt >= APOGEE_ALTITUDE:
            self._switch_to_glide()
        elif self.apogee_reached:
            self._glide_with_gravity(time_step)

        self._update_position(time_step, env)

        if not self._has_hit_ground():
            self.schedule_event(MovementEvent, env, time_step=1)

    def _apply_thrust(self, time_step):
        """Apply thrust during the powered boost phase."""
        missile_logger.info(f"Missile {self.entity_id} is in powered boost flight.")
        current_speed = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2 + self.velocity[2]**2)

        # Ensure speed does not exceed max_velocity
        if current_speed < self.max_velocity:
            acceleration_factor = min(self.acceleration_rate * time_step, self.max_velocity - current_speed)
            self.velocity[0] += acceleration_factor * math.cos(math.radians(self.orientation[1]))
            self.velocity[1] += acceleration_factor * math.sin(math.radians(self.orientation[1]))
            
            # Only apply vertical thrust if missile is climbing
            if self.orientation[0] > 0:  # Positive pitch means climbing
                self.velocity[2] += (self.acceleration_rate * math.sin(math.radians(self.orientation[0])) - self.gravity) * time_step
            else:
                self.velocity[2] -= self.gravity * time_step

        self.fuel -= time_step * 10  # Decrease fuel at a realistic rate

        if self.fuel <= 0:
            self._switch_to_glide()

    def _adjust_pitch_for_boost_phase(self):
        """Adjust the pitch of the missile during the boost phase to gradually increase altitude."""
        # The pitch will gradually lower faster to allow horizontal speed buildup
        self.orientation[0] = max(10, self.orientation[0] - 1.5)  # Faster pitch decrease
        missile_logger.info(f"Missile {self.entity_id} adjusted pitch during boost phase: {self.orientation[0]} degrees")

    def _switch_to_glide(self):
        """Switch to glide mode when apogee is reached or fuel runs out."""
        missile_logger.info(f"Missile {self.entity_id} switching to glide mode at altitude {self.alt}.")
        self.boost_phase = False
        self.apogee_reached = True
        self._set_glide_orientation()

    def _glide_with_gravity(self, time_step):
        """Glide towards the target with gravity affecting vertical velocity."""
        missile_logger.info(f"Missile {self.entity_id} is gliding towards the target.")
        
        # Calculate current horizontal speed (ignore Z for glide)
        current_speed = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
        deceleration = self.deceleration_rate * time_step
        new_speed = max(current_speed - deceleration, 0)
        if current_speed != 0:
            scale_factor = new_speed / current_speed
            self.velocity[0] *= scale_factor
            self.velocity[1] *= scale_factor

        # Ensure the missile descends during glide
        self.velocity[2] -= (self.gravity * time_step)

        # If the missile is high in altitude, ensure pitch gradually adjusts downwards
        if self.alt <= 50000:  # Example threshold for terminal phase (~50 km altitude)
            self._adjust_for_terminal_phase()
        else:
            # Gradually lower the pitch for glide (ensuring it points downward)
            self.orientation[0] = max(self.orientation[0] - 0.5, -45)  # Decrease pitch more aggressively if needed

        missile_logger.info(f"Missile {self.entity_id} velocity during glide: {self.velocity}")
        self._log_position()

    def _set_glide_orientation(self):
        """Adjust missile orientation to glide towards the target."""
        distance, bearing = calculate_distance_and_bearing(self.lat, self.lon, self.target.lat, self.target.lon)
        self.orientation[1] = bearing  # Set yaw towards target
        missile_logger.info(f"Missile {self.entity_id} adjusted orientation for glide: pitch {self.orientation[0]}, yaw {self.orientation[1]}")

    def _adjust_for_terminal_phase(self):
        """Adjust the missile for the steep descent in the terminal phase."""
        missile_logger.info(f"Missile {self.entity_id} entering terminal phase, adjusting pitch to {TERMINAL_PHASE_PITCH}.")
        self.orientation[0] = TERMINAL_PHASE_PITCH  # Steep descent pitch

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