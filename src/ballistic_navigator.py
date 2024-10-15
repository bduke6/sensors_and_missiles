import pymap3d as pm
import logging
import math

from logging import FileHandler

# Set up a separate logger for missile_1 ballistic navigation
bal_nav_logger = logging.getLogger("missile_1_bal_nav")
bal_nav_logger.setLevel(logging.INFO)

# Handler for missile_1 specific ballistic navigation logs
missile_1_handler = FileHandler("logs/missile_1_bal_nav.log")
missile_1_handler.setLevel(logging.INFO)

# Custom format to include phase and parameter information
formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - [%(phase)s] %(message)s')
missile_1_handler.setFormatter(formatter)
bal_nav_logger.addHandler(missile_1_handler)

class BallisticNavigator:
    def __init__(self, entity, target_lat, target_lon):
        self.entity = entity
        self.target_lat = target_lat
        self.target_lon = target_lon
        self.target_alt = 0  # Assume ground-level target
        self.g = 9.81  # Gravity in m/s^2
        self.min_range = 1000  # Set a minimum threshold range

        # Calculate initial AER (Azimuth, Elevation, Range) from entity to target
        self.calculate_initial_aer()

    def calculate_initial_aer(self):

        # Your initial setup logic, plus logging with phase tag
        self.phase = "INITIAL_CALC"
        bal_nav_logger.info(
            f"Calculating initial AER for {self.entity.entity_id}: "
            f"lat: {self.entity.lat}, lon: {self.entity.lon}, altitude: {self.entity.alt}",
            extra={'phase': self.phase}
        )

        # Calculate target ECEF position from lat/lon
        self.target_x, self.target_y, self.target_z = pm.geodetic2ecef(self.target_lat, self.target_lon, self.target_alt)

        # Calculate AER from current entity position to the target
        azimuth, elevation, range_to_target = pm.ecef2aer(
            self.target_x, self.target_y, self.target_z,
            lat0=self.entity.lat, lon0=self.entity.lon, h0=self.entity.alt, deg=True
        )

        if range_to_target < self.min_range:
            range_to_target = self.min_range
            logging.warning(f"Missile {self.entity.entity_id} target is too close; range set to minimum threshold.")

        # Update entity heading to point to the target
        self.entity.heading = azimuth
        self.range_to_target = range_to_target
        logging.info(f"Calculated initial range to target for {self.entity.entity_id}: {self.range_to_target:.2f} meters, heading {azimuth:.2f} degrees.")

        # Schedule initial launch event
        launch_params = {
            'heading': self.entity.heading,
            'altitude': 0,
            'speed': 500  # Initial non-zero speed to begin movement
        }
        self.entity.schedule_event({
            'type': 'nav',
            'time': self.entity.environment.current_time,
            'entity': self.entity,
            'params': launch_params
        })
        logging.info(f"Scheduled initial launch for {self.entity.entity_id} with altitude {launch_params['altitude']} meters and speed {launch_params['speed']} m/s.")

    def calculate_ballistic_trajectory(self):
        boost_end_time = self.schedule_boost_phase()
        midcourse_end_time = self.schedule_midcourse_phase(boost_end_time)
        self.schedule_descent_phase(midcourse_end_time)

    def schedule_boost_phase(self):
        # Set the desired upward trajectory by directly assigning a high value to the z velocity component
        test_z_velocity = 1000  # Assign a higher test value for vertical speed

        # Keep azimuth and set elevation to 90 degrees for purely vertical movement
        azimuth = self.entity.heading  # Current heading
        elevation = 90  # Vertical ascent angle

        # Simplified ECEF velocity with a constant z component for rapid ascent
        x_ecef_vel, y_ecef_vel, z_ecef_vel = 0, 0, test_z_velocity  # Set only z component

        # Log the assigned values for debugging
        logging.info(f"[Boost Phase] Testing vertical ascent with constant z velocity: {z_ecef_vel:.2f} m/s.")

        # Set the initial boost parameters with the adjusted velocity vector
        boost_params = {
            'heading': azimuth,
            'altitude': self.entity.alt + 1000,  # Expected altitude increment (arbitrary for testing)
            'velocity_vector': (x_ecef_vel, y_ecef_vel, z_ecef_vel)
        }

        # Schedule the boost phase navigation event immediately to check ascent behavior
        boost_time = self.entity.environment.current_time + 1
        self.entity.schedule_event({
            'type': 'nav',
            'time': boost_time,
            'entity': self.entity,
            'params': boost_params
        })
        
        logging.info(f"[Boost Phase] Scheduled test boost with altitude gain for rapid vertical ascent at time {boost_time:.2f}.")

        return boost_time



    def calculate_boost_speed(self, boost_duration):
        return self.g * boost_duration

    def schedule_midcourse_phase(self, boost_end_time):
        apogee = self.range_to_target * 0.15
        midcourse_duration = math.sqrt(2 * apogee / self.g)
        midcourse_time = boost_end_time  # Start immediately after boost ends
        midcourse_speed = self.calculate_midcourse_speed()

        midcourse_params = {
            'heading': self.entity.heading,
            'altitude': apogee,
            'speed': midcourse_speed
        }
        self.entity.schedule_event({
            'type': 'nav',
            'time': midcourse_time,
            'entity': self.entity,
            'params': midcourse_params
        })
        logging.info(f"Scheduled midcourse phase for {self.entity.entity_id} with apogee {apogee:.2f} meters, speed {midcourse_speed:.2f} m/s at time {midcourse_time:.2f}.")
        return midcourse_time + midcourse_duration  # Return the end time of the midcourse phase

    def calculate_midcourse_speed(self):
        return self.calculate_boost_speed(math.sqrt(2 * 10000 / self.g)) * 0.8

    def schedule_descent_phase(self, midcourse_end_time):
        descent_params = {
            'heading': self.entity.heading,
            'altitude': 0,
            'speed': 3000
        }
        descent_start_time = midcourse_end_time  # Start immediately after midcourse ends

        self.entity.schedule_event({
            'type': 'nav',
            'time': descent_start_time,
            'entity': self.entity,
            'params': descent_params
        })
        logging.info(f"Scheduled descent phase for {self.entity.entity_id} with target altitude {descent_params['altitude']} meters, speed {descent_params['speed']} m/s at time {descent_start_time:.2f}.")
