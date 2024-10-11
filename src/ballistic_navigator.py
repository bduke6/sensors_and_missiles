import pymap3d as pm
import logging
import math

class BallisticNavigator:
    def __init__(self, entity, target_lat, target_lon):
        self.entity = entity
        self.target_lat = target_lat
        self.target_lon = target_lon
        self.target_alt = 0  # Assume ground-level target
        self.g = 9.81  # Gravity in m/s^2

    def calculate_ballistic_trajectory(self):
        # Step 1: Dynamically schedule the boost phase duration based on the distance to target
        self.schedule_boost_phase()

        # Step 2: Set transition to midcourse at apogee
        self.schedule_midcourse_phase()

        # Step 3: Schedule descent and final adjustments to impact the target
        self.schedule_descent_phase()

    def schedule_boost_phase(self):
        # Calculate boost duration based on launch characteristics and range
        # Estimate boost altitude and velocity for apogee planning
        range_to_target = self.calculate_range_to_target()
        boost_duration = self.estimate_boost_duration(range_to_target)
        
        # Set initial ascent parameters (vertical boost)
        boost_params = {
            'heading': 90,   # Straight up
            'speed': 700,    # Example initial speed
            'altitude': self.calculate_apogee(range_to_target)  # Apogee as target altitude for boost
        }
        self.entity.navigator(boost_params)  # Call navigator to initiate the boost phase

        # Schedule the event in environment after boost duration
        self.entity.schedule_event({
            'type': 'nav',
            'time': self.entity.environment.current_time + boost_duration,
            'entity': self.entity,
            'params': boost_params
        })
        logging.info(f"Scheduled boost phase for {self.entity.entity_id} with duration {boost_duration} seconds.")

    def schedule_midcourse_phase(self):
        # Estimate the midcourse phase timing
        midcourse_duration = self.estimate_midcourse_duration()
        midcourse_params = {
            'heading': self.calculate_midcourse_heading(),
            'speed': 2500,  # Midcourse speed as example
            'altitude': self.calculate_apogee(self.calculate_range_to_target())  # Apogee for midcourse phase
        }
        
        # Schedule midcourse event
        self.entity.schedule_event({
            'type': 'nav',
            'time': self.entity.environment.current_time + midcourse_duration,
            'entity': self.entity,
            'params': midcourse_params
        })
        logging.info(f"Midcourse phase scheduled for {self.entity.entity_id} at time {midcourse_duration}.")

    def schedule_descent_phase(self):
        # Calculate when descent phase should begin
        descent_start_time = self.estimate_descent_start_time()
        descent_params = {
            'heading': self.calculate_descent_heading(),
            'speed': 3500,  # High-speed terminal descent
            'altitude': self.target_alt
        }

        # Schedule descent event
        self.entity.schedule_event({
            'type': 'nav',
            'time': descent_start_time,
            'entity': self.entity,
            'params': descent_params
        })
        logging.info(f"Descent phase scheduled for {self.entity.entity_id} at time {descent_start_time}.")

    # Helper functions
    def calculate_range_to_target(self):
        # Calculate range in meters to target based on initial coordinates
        _, _, range_to_target = pm.geodetic2aer(
            self.entity.lat, self.entity.lon, self.entity.alt,
            self.target_lat, self.target_lon, self.target_alt
        )
        return range_to_target

    def calculate_apogee(self, range_to_target):
        # Roughly calculate apogee based on range
        return 0.1 * range_to_target  # Simplified approach for apogee height

    def estimate_boost_duration(self, range_to_target):
        # Estimate boost phase duration based on range
        return min(150, range_to_target / 50)  # Simplified calculation, could use velocity profile

    def estimate_midcourse_duration(self):
        # Based on apogee altitude and gravity for freefall approximation
        apogee = self.calculate_apogee(self.calculate_range_to_target())
        return math.sqrt((2 * apogee) / self.g)

    def estimate_descent_start_time(self):
        # Start descent based on estimated total flight time minus descent phase duration
        total_flight_time = self.estimate_midcourse_duration() * 2  # Symmetric path assumption
        descent_duration = total_flight_time / 3  # Simplified split for descent phase
        return self.entity.environment.current_time + total_flight_time - descent_duration

    def calculate_midcourse_heading(self):
        # Calculate heading halfway to target based on great circle
        _, az, _ = pm.geodetic2aer(self.entity.lat, self.entity.lon, self.entity.alt,
                                   self.target_lat, self.target_lon, self.target_alt)
        return az

    def calculate_descent_heading(self):
        # Heading directly to the target
        _, az, _ = pm.geodetic2aer(self.entity.lat, self.entity.lon, self.entity.alt,
                                   self.target_lat, self.target_lon, self.target_alt)
        return az
