import pymap3d as pm
import logging
import math

class BallisticNavigator:
    def __init__(self, entity, target_lat, target_lon):
        self.entity = entity
        self.target_lat = target_lat
        self.target_lon = target_lon
        self.target_alt = 0  # Target at ground level
        self.g = 9.81  # Gravity in m/s^2
        self.horizontal_velocity = 2500  # Horizontal speed in m/s
        self.vertical_velocity = 5000  # Initial upward speed in m/s
        self.time_step = 1  # Simulation time step in seconds
        self.apogee_reached = False  # Track if apogee is reached

        # Calculate the distance to the target and apogee
        self.distance_to_target = self.calculate_distance_to_target()
        self.apogee = self.calculate_apogee()

        # Set the initial heading toward the target
        self.calculate_initial_heading()

        # Adjust the launch angle dynamically based on the distance and apogee
        self.launch_angle = self.calculate_launch_angle()

    def calculate_distance_to_target(self):
        # Calculate horizontal distance to the target
        _, _, distance = pm.geodetic2aer(
            self.target_lat, self.target_lon, self.target_alt,
            self.entity.lat, self.entity.lon, self.entity.alt,
            deg=True
        )
        return distance

    def calculate_apogee(self):
        # Set apogee as a function of distance (you can modify this as needed)
        return 0.15 * self.distance_to_target  # Example factor

    def calculate_launch_angle(self):
        # Calculate the launch angle based on apogee and distance to target
        return math.degrees(math.atan((4 * self.apogee) / self.distance_to_target))

    def calculate_initial_heading(self):
        # Determine initial azimuth to target in degrees
        azimuth, _, _ = pm.geodetic2aer(
            self.target_lat, self.target_lon, self.target_alt,
            self.entity.lat, self.entity.lon, self.entity.alt,
            deg=True
        )
        self.entity.heading = azimuth
        logging.info(f"Initial heading for {self.entity.entity_id} set to {self.entity.heading:.2f} degrees")

    def initiate_ballistic_flight(self):
        # Schedule the boost phase
        boost_end_time = self.schedule_boost_phase()
        # Schedule the transition to midcourse and descent
        self.schedule_midcourse_and_descent(boost_end_time)

    def schedule_boost_phase(self):
        # Vertical boost phase, with simultaneous horizontal movement
        boost_duration = 5  # Duration for boost phase in seconds
        boost_end_time = self.entity.environment.current_time + boost_duration
        # Set initial ECEF velocity vector based on launch angle
        x_vel, y_vel, z_vel = self.calculate_velocity_vector(self.horizontal_velocity, self.vertical_velocity)
        self.entity.velocity_vector_ecef = (x_vel, y_vel, z_vel)
        self.schedule_move(boost_end_time, "Boost Phase")
        return boost_end_time

    def schedule_midcourse_and_descent(self, boost_end_time):
        # Transition to descent, with realistic altitude decrease
        duration = 30  # Midcourse duration in seconds
        end_time = boost_end_time + duration
        # Adjust velocity for descent phase
        x_vel, y_vel, z_vel = self.calculate_velocity_vector(self.horizontal_velocity, -self.g * self.time_step)
        self.entity.velocity_vector_ecef = (x_vel, y_vel, z_vel)
        self.schedule_move(end_time, "Midcourse & Descent Phase")
    
    def schedule_move(self, event_time, phase):
        # Update heading toward target before each move
        self.update_heading()
        self.log_position_update(phase)
        
        # Schedule the move event with the main event queue
        self.entity.schedule_event({
            'type': 'move',
            'time': event_time,
            'entity': self.entity,
            'params': {
                'velocity_vector': self.entity.velocity_vector_ecef,
                'altitude': max(self.entity.alt, 0)  # Prevent underground
            }
        })
        logging.info(f"Scheduled {phase} move for {self.entity.entity_id} at time {event_time}")
        
        # Schedule the next move event based on the time step
        next_event_time = event_time + self.time_step
        if self.entity.alt > 0:  # Continue if above ground
            self.entity.schedule_event({
                'type': 'bal_nav',  # Re-trigger ballistic navigation
                'time': next_event_time,
                'entity': self.entity,
                'params': {'tgt_lat': self.target_lat, 'tgt_lon': self.target_lon}
            })

    def calculate_velocity_vector(self, horizontal_speed, vertical_speed):
        # Get ECEF velocity components from AER
        azimuth = self.entity.heading
        x_ecef_vel, y_ecef_vel, z_ecef_vel = pm.aer2ecef(
            az=azimuth,
            el=self.launch_angle,  # Use launch angle for the vertical component
            srange=horizontal_speed,
            lat0=self.entity.lat,
            lon0=self.entity.lon,
            alt0=self.entity.alt,
            deg=True
        )
        # Add vertical velocity component directly to 'up' component in ENU frame
        up_velocity = vertical_speed - self.g * self.time_step if self.apogee_reached else vertical_speed
        x_ecef_vel += up_velocity

        return (x_ecef_vel - self.entity.ecef_x, y_ecef_vel - self.entity.ecef_y, z_ecef_vel - self.entity.ecef_z)

    def update_heading(self):
        # Calculate heading update toward target
        azimuth, _, _ = pm.geodetic2aer(
            self.target_lat, self.target_lon, self.target_alt,
            self.entity.lat, self.entity.lon, self.entity.alt,
            deg=True
        )
        self.entity.heading = azimuth

    def log_position_update(self, phase):
        # Log entity position for map logger
        heading_str = f"{self.entity.heading:.6f}" if self.entity.heading is not None else "N/A"
        self.entity.map_logger.info(
            f"{self.entity.environment.current_time},{self.entity.entity_id},{self.entity.lat:.6f},{self.entity.lon:.6f},{heading_str},{max(self.entity.alt, 0):.6f}"
        )
        logging.info(f"{self.entity.entity_id} - {phase} at time {self.entity.environment.current_time}")
