import math
import logging
from calculations import geodetic_to_ecef, ecef_to_geodetic, calculate_distance_and_bearing
from events import MovementEvent  # Import needed event classes

# Create a logger for the missile
missile_logger = logging.getLogger('entity')

# Constants
APOGEE_ALTITUDE = 800000  # Apogee for DF-21D in meters (~800 km)
BOOST_PHASE_DURATION = 120  # Boost phase lasts for 2 minutes (120 seconds)
GROUND_TOLERANCE = 1.0  # Tolerance for ground impact detection
TERMINAL_PHASE_PITCH = -80  # Steep descent in terminal phase
MAX_VELOCITY = 8000  # Updated max velocity during powered flight for realistic speeds (m/s)
GLIDE_DECELERATION_RATE = 1.5  # Updated deceleration rate during glide phase
TERMINAL_PHASE_ALTITUDE = 70000  # Altitude threshold for entering the terminal phase (~70 km)

class Missile:
    def __init__(self, lat, lon, alt, velocity, orientation, entity_id=None, fuel=100, max_velocity=MAX_VELOCITY):
        self.lat = lat  # Latitude
        self.lon = lon  # Longitude
        self.alt = alt  # Altitude
        self.velocity = velocity  # Velocity vector [vx, vy, vz]
        self.orientation = [math.radians(orientation[0]), math.radians(orientation[1]), math.radians(orientation[2])]  # Convert orientation to radians
        self.entity_id = entity_id if entity_id else self.generate_unique_id()
        self.max_velocity = max_velocity  # Maximum velocity in powered flight
        self.fuel = fuel
        self.acceleration_rate = 300  # Updated acceleration rate for boost phase
        self.deceleration_rate = GLIDE_DECELERATION_RATE  # Updated deceleration rate in no-power flight
        self.gravity = 9.81  # Gravity value for downward acceleration
        self.apogee_reached = False
        self.boost_phase = True
        self.midcourse_phase = False  # Introduced midcourse phase
        self.reentry_phase = False  # Introduced reentry phase
        self.terminal_phase = False  # Introduced terminal phase
        self.target = None  # To store the target's coordinates
        self.elapsed_time = 0  # Track time since launch

        # Initialize ECEF coordinates using geodetic to ECEF conversion
        self.X, self.Y, self.Z = geodetic_to_ecef(self.lat, self.lon, self.alt)

    def launch(self, target, env):
        """Initiate missile launch."""
        self.target = target
        missile_logger.info(f"Missile {self.entity_id} launched at target {target.entity_id}")

        # Calculate initial bearing (yaw) to the target
        _, bearing_to_target = calculate_distance_and_bearing(self.lat, self.lon, self.target.lat, self.target.lon)
        missile_logger.info(f"Initial bearing to target: {bearing_to_target:.2f} degrees")

        # Set yaw to the initial bearing
        self.orientation[1] = bearing_to_target  # Yaw is set to the bearing

        # **Set initial pitch to 90 degrees for vertical climb**
        self.orientation[0] = 90  # Pitch is set to near-vertical

        # Convert yaw to radians for use in velocity calculation
        yaw_radians = math.radians(self.orientation[1])

        # Set initial speed and calculate components based on pitch and yaw
        initial_speed = 300.0  # Speed during launch (adjust as needed)
        pitch_radians = math.radians(self.orientation[0])

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

        # Calculate the current bearing and distance to the target
        distance, bearing_to_target = calculate_distance_and_bearing(self.lat, self.lon, self.target.lat, self.target.lon)

        missile_logger.info(f"Target lat: {self.target.lat}, lon: {self.target.lon}")
        missile_logger.info(f"Distance to target: {distance:.2f} meters, bearing to target: {bearing_to_target:.2f} degrees")

        # Convert bearing to radians
        bearing_to_target_radians = math.radians(bearing_to_target)

        # Adjust yaw towards the target during flight
        yaw_diff = bearing_to_target_radians - self.orientation[1]

        if abs(yaw_diff) > math.radians(1.0):  # Adjust yaw only if the difference is greater than 1.0 degrees in radians
            yaw_step = min(abs(yaw_diff), math.radians(1.0)) * (1 if yaw_diff > 0 else -1)
            self.orientation[1] += yaw_step
            missile_logger.info(f"self.orientation[1]: {math.degrees(self.orientation[1])} degrees, yaw_step: {math.degrees(yaw_step)} degrees")
        else:
            missile_logger.info(f"Yaw is close to target bearing: {bearing_to_target:.2f} degrees, no significant adjustment needed.")


        # Boost phase (climb to apogee)
        if self.boost_phase:
            if self.elapsed_time <= BOOST_PHASE_DURATION and self.fuel > 0:
                self._apply_thrust(time_step)
                self._adjust_pitch_for_boost_phase()
            else:
                self._switch_to_midcourse_phase()

        # Ballistic flight phase (post-boost, pre-reentry)
        elif not self.apogee_reached:
            self._ballistic_flight(time_step)
            if self.alt >= APOGEE_ALTITUDE:
                self.apogee_reached = True
                missile_logger.info(f"Missile {self.entity_id} has reached apogee.")
            else:
                self._adjust_pitch_for_descent()

        # Reentry phase (descent)
        elif self.apogee_reached:
            self._descent_to_target(time_step)

        # Update missile position
        self._update_position(time_step, env)

        # Check for ground impact
        if not self._has_hit_ground():
            self.schedule_event(MovementEvent, env, time_step=1)
        else:
            missile_logger.info(f"Missile {self.entity_id} has hit the ground at altitude {self.alt}. Terminating movement.")

    def _has_hit_ground(self):
        """Check if the missile has hit the ground."""
        _, _, alt = ecef_to_geodetic(self.X, self.Y, self.Z)  # Convert current ECEF position to geodetic
        missile_logger.info(f"Missile altitude: {alt:.2f} meters")
        return alt <= GROUND_TOLERANCE  # If altitude is less than or equal to ground tolerance, missile has hit ground

    def _apply_thrust(self, time_step):
        """Apply thrust during the powered boost phase."""
        missile_logger.info(f"Missile {self.entity_id} is in powered boost flight.")
        
        # Calculate current speed (total speed combining X, Y, Z velocity components)
        current_speed = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2 + self.velocity[2]**2)

        missile_logger.info(f"Missile {self.entity_id} current speed: {current_speed:.2f} m/s")

        # Ensure speed does not exceed max_velocity
        if current_speed < self.max_velocity:
            # Apply acceleration to all velocity components, considering current orientation
            pitch_radians = math.radians(self.orientation[0])
            yaw_radians = math.radians(self.orientation[1])

            # Calculate thrust in horizontal and vertical components
            thrust_horizontal = self.acceleration_rate * math.cos(pitch_radians) * time_step
            thrust_vertical = self.acceleration_rate * math.sin(pitch_radians) * time_step

            missile_logger.info(f"thrust_horizontal: {thrust_horizontal} /////////////////////////////////////////////////// thrust_vertical: {thrust_vertical}")

            # Apply thrust to X and Y components (horizontal direction)
            self.velocity[0] += thrust_horizontal * math.cos(yaw_radians)
            self.velocity[1] += thrust_horizontal * math.sin(yaw_radians)

            # Apply thrust to the Z component (vertical direction), and account for gravity
            self.velocity[2] += (thrust_vertical - self.gravity) * time_step

        # Reduce fuel based on time step
        self.fuel -= time_step * 10  # Adjust fuel consumption




    def _adjust_pitch_for_descent(self):
        """Gradually adjust the pitch downwards after apogee."""
        # After apogee, gradually pitch the missile downward to align with the descent
        self.orientation[0] = max(self.orientation[0] - 1, -45)  # Gradual adjustment towards -45 degrees
        missile_logger.info(f"Missile {self.entity_id} adjusted pitch during descent: {self.orientation[0]} degrees")

    def _descent_to_target(self, time_step):
        """Handle the missile's descent after apogee."""
        missile_logger.info(f"Missile {self.entity_id} in descent phase towards target.")
        
        # The missile is now descending rapidly, gravity continues to act on it
        # Velocity should be primarily in the Z (vertical) direction at this point
        self.velocity[0] = 0  # Zero out horizontal velocity
        self.velocity[1] = 0  # Zero out horizontal velocity
        self.velocity[2] -= self.gravity * time_step  # Continue falling due to gravity
        
        # Ensure pitch remains -90 degrees during descent
        self.orientation[0] = -90  # Fully downward pitch

        missile_logger.info(f"Missile {self.entity_id} velocity during descent: {self.velocity}")
        self._log_position()



    def _adjust_pitch_for_boost_phase(self):
        """Adjust the pitch of the missile during the boost phase to gradually increase altitude."""
        # Start with a near-vertical pitch (90 degrees) and reduce it slowly
        self.orientation[0] = max(45, self.orientation[0] - 0.5)  # Gradually reduce pitch, but not below 45 degrees
        missile_logger.info(f"Missile {self.entity_id} adjusted pitch during boost phase: {self.orientation[0]} degrees")




    def _switch_to_midcourse_phase(self):
        """Switch to the ballistic midcourse phase after the boost phase completes."""
        missile_logger.info(f"Missile {self.entity_id} switching to midcourse phase at altitude {self.alt}.")
        self.boost_phase = False
        self.midcourse_phase = True

   

    def _ballistic_flight(self, time_step):
        """Ballistic flight during the midcourse phase after boost."""
        missile_logger.info(f"Missile {self.entity_id} in midcourse ballistic phase.")
        
        # In ballistic flight, no additional thrust is applied
        # Gravity will gradually pull the missile down
        self.velocity[2] -= self.gravity * time_step

        missile_logger.info(f"Missile {self.entity_id} ballistic velocity: {self.velocity}")
        self._log_position()

    def _switch_to_reentry_phase(self):
        """Switch to the reentry phase after apogee, starting to descend towards target."""
        missile_logger.info(f"Missile {self.entity_id} switching to reentry phase.")
        self.midcourse_phase = False
        self.reentry_phase = True
        self._adjust_for_reentry()

    def _adjust_for_reentry(self):
        """Adjust the missile for a steep descent during the reentry phase."""
        missile_logger.info(f"Missile {self.entity_id} adjusting pitch for reentry.")
        self.orientation[0] = max(self.orientation[0] - 0.5, -45)  # Steep pitch for reentry

    def _switch_to_terminal_phase(self, time_step):
        """Switch to terminal phase for final steep descent."""
        missile_logger.info(f"Missile {self.entity_id} switching to terminal phase.")
        self.reentry_phase = False
        self.terminal_phase = True
        self._adjust_for_terminal_phase()

    def _adjust_for_terminal_phase(self):
        """Adjust for terminal phase (steep descent)."""
        missile_logger.info(f"Missile {self.entity_id} entering terminal phase.")
        # Ensure the pitch is directly downward during terminal phase
        self.orientation[0] = TERMINAL_PHASE_PITCH  # -80 to -90 degrees for steep descent
        self.velocity[0] *= 0.95  # Reduce horizontal velocity further
        self.velocity[1] *= 0.95  # Reduce horizontal velocity further
        self.velocity[2] = min(self.velocity[2] + 100, MAX_VELOCITY)  # Ensure rapid descent

    def _update_position(self, time_step, env):
        """Update the missile position based on its velocity."""
        # Update ECEF coordinates based on current velocity
        self.X += self.velocity[0] * time_step
        self.Y += self.velocity[1] * time_step
        self.Z += self.velocity[2] * time_step

        # Convert ECEF back to geodetic (lat, lon, alt)
        self.lat, self.lon, self.alt = ecef_to_geodetic(self.X, self.Y, self.Z)
        
        # Log the updated position
        missile_logger.info(f"Missile {self.entity_id} moved to ECEF ({self.X}, {self.Y}, {self.Z})")
        missile_logger.info(f"Missile {self.entity_id} moved to lat: {self.lat}, lon: {self.lon}, alt: {self.alt}")
        missile_logger.info(f"Missile {self.entity_id} orientation: pitch: {self.orientation[0]}, yaw: {self.orientation[1]}, roll: {self.orientation[2]}")

    def _has_hit_ground(self):
        """Check if the missile has hit the ground."""
        _, _, alt = ecef_to_geodetic(self.X, self.Y, self.Z)  # Convert current ECEF position to geodetic
        missile_logger.info(f"Missile {self.entity_id} altitude: {alt} meters")  # Log the altitude
        return alt <= GROUND_TOLERANCE  # If altitude is less than or equal to ground tolerance, missile has hit ground

    def schedule_event(self, event_type, env, time_step):
        """Schedule the next event for the missile."""
        next_event_time = env.current_time + time_step
        event = event_type(next_event_time, self, time_step)
        env.schedule_event(event)
        missile_logger.info(f"Missile {self.entity_id} scheduled event: {event_type.__name__} at time {next_event_time}")
    
    def handle_event(self, event, env):
        """Handle events like movement."""
        if isinstance(event, MovementEvent):
            self.move(event.time_step, env)

    def _log_position(self):
        """Log the missile's current position and orientation."""
        missile_logger.info(f"Missile {self.entity_id} moved to ECEF ({self.X}, {self.Y}, {self.Z})")
        missile_logger.info(f"Missile {self.entity_id} moved to lat: {self.lat}, lon: {self.lon}, alt: {self.alt}")
        missile_logger.info(f"Missile {self.entity_id} orientation: pitch: {self.orientation[0]}, yaw: {self.orientation[1]}, roll: {self.orientation[2]}")

    def generate_unique_id(self):
        """Generate a unique identifier for the missile."""
        import uuid
        return str(uuid.uuid4())

