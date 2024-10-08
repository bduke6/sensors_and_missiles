import pymap3d as pm
import logging
from simulation_event import SimulationEvent  

class Entity:
    def __init__(self, config, environment):
        self.entity_id = config['entity_id']
        self.lat = config['lat']
        self.lon = config['lon']
        self.alt = config['alt']
        self.environment = environment
        self.events = config.get('events', [])
        self.map_logger = logging.getLogger('map_logger')
        self.velocity_vector_ecef = None
        self.is_underway = False
        self.underway_time = 0
        self.mark_time = 0
        self.target_heading = None
        self.target_speed = None
        self.target_altitude = None
        self.speed = 0
        logging.info(f"Entity created: {self.entity_id}")

        # Initialize ECEF position
        self.ecef_x, self.ecef_y, self.ecef_z = pm.geodetic2ecef(self.lat, self.lon, self.alt)
        logging.info(f"{self.entity_id} initial ECEF Position: x={self.ecef_x}, y={self.ecef_y}, z={self.ecef_z}")

        # Schedule first event
        if self.events:
            self.schedule_event({
                'type': self.events[0]['type'],
                'time': self.events[0]['start_time'],
                'entity': self,
                'params': self.events[0]['params']
            })

    def process_event(self, event):
        logging.info(f"Processing event for {self.entity_id}: {event}")
        if event['type'] == 'commo':
            self.commo(event['params'])
        elif event['type'] == 'move':
            self.move()
        elif event['type'] == 'navigator_check':
            self.navigator_check()

    def commo(self, params):
        message_type = params.get('message_type')
        if message_type == 'nav':
            logging.info(f"Received navigation message for {self.entity_id}")
            self.navigator(params)

    def navigator(self, params):
        self.target_heading = params['heading']
        self.target_speed = params['speed']
        self.target_altitude = params.get('altitude', self.alt)
        self.speed = self.target_speed
        self.heading = self.target_heading
        dt = 1

        # Calculate ECEF velocity vector based on target heading and speed
        x_ecef_vel, y_ecef_vel, z_ecef_vel = pm.aer2ecef(
            az=self.target_heading,
            el=0,
            srange=self.speed * dt,
            lat0=self.lat,
            lon0=self.lon,
            alt0=self.alt,
            deg=True
        )

        self.velocity_vector_ecef = (x_ecef_vel - self.ecef_x, y_ecef_vel - self.ecef_y, z_ecef_vel - self.ecef_z)
        self.is_underway = True
        self.underway_time = 1

        # Clear any existing move events before scheduling
        self.clear_scheduled_events(event_type='move')

        # Schedule initial move event with the updated velocity vector
        self.schedule_event({
            'type': 'move',
            'time': self.environment.current_time + dt,
            'entity': self,
            'params': {
                'velocity_vector': self.velocity_vector_ecef,
                'altitude': self.target_altitude
            }
        })
        logging.info(f"Navigator set initial velocity vector: {self.velocity_vector_ecef}")

        # Schedule first navigator check after a short delay to allow for adjustments
        self.schedule_event({
            'type': 'navigator_check',
            'time': self.environment.current_time + dt + 5,
            'entity': self,
            'params': {}
        })

    def move(self):
        """Move function only applies the velocity vector without adjusting altitude."""
        if not self.velocity_vector_ecef:
            logging.warning(f"No velocity vector available for {self.entity_id}, skipping move.")
            return

        dt = 1
        self.underway_time += dt
        self.mark_time += dt

        # Apply velocity vector to position
        self.ecef_x += self.velocity_vector_ecef[0] * dt
        self.ecef_y += self.velocity_vector_ecef[1] * dt
        self.ecef_z += self.velocity_vector_ecef[2] * dt

        # Convert ECEF coordinates to geodetic
        self.lat, self.lon, self.alt = pm.ecef2geodetic(self.ecef_x, self.ecef_y, self.ecef_z)

        # Log current state for visualization
        self.map_logger.info(f"{self.environment.current_time},{self.entity_id},{self.lat:.6f},{self.lon:.6f},{self.heading:.6f},{self.alt:.6f}")

        # Schedule next move event if not already scheduled
        if not self.environment.is_event_scheduled('move', self.entity_id, self.environment.current_time + dt):
            self.schedule_event({
                'type': 'move',
                'time': self.environment.current_time + dt,
                'entity': self,
                'params': {'velocity_vector': self.velocity_vector_ecef, 'altitude': self.alt}
            })

    def navigator_check(self):
        logging.info(f"Navigator checking course for {self.entity_id}.")

        target_altitude = self.target_altitude
        altitude_deviation = self.alt - target_altitude

        # Define a tolerance range for altitude adjustments
        tolerance_range = 2  # Smaller tolerance range to avoid oscillations
        correction_delay = 10 if abs(altitude_deviation) < 10 else 3

        # Check if altitude deviation exceeds tolerance
        if abs(altitude_deviation) > tolerance_range:
            logging.info(f"{self.entity_id} altitude deviation = {altitude_deviation:.2f}. Adjusting altitude.")

            # Calculate a more direct correction to bring altitude to target
            correction_elevation = -0.1 * (altitude_deviation / abs(altitude_deviation))  # Apply fixed rate toward target

            # Recalculate ECEF coordinates based on this correction
            x_ecef_corr, y_ecef_corr, z_ecef_corr = pm.aer2ecef(
                az=self.heading,
                el=correction_elevation,
                srange=self.speed,
                lat0=self.lat,
                lon0=self.lon,
                alt0=self.alt,
                deg=True
            )

            # Apply correction vector directly
            self.velocity_vector_ecef = (
                (x_ecef_corr - self.ecef_x) * 0.5,  # Scale corrections to avoid overshooting
                (y_ecef_corr - self.ecef_y) * 0.5,
                (z_ecef_corr - self.ecef_z) * 0.5
            )

            # Clear previous move events and schedule the updated move event
            self.clear_scheduled_events(event_type='move')
            self.schedule_event({
                'type': 'move',
                'time': self.environment.current_time + 1,
                'entity': self,
                'params': {'velocity_vector': self.velocity_vector_ecef, 'altitude': target_altitude}
            })

        # Schedule the next navigator check with adaptive delay
        if self.is_underway:
            self.schedule_event({
                'type': 'navigator_check',
                'time': self.environment.current_time + correction_delay,
                'entity': self,
                'params': {}
            })



    def clear_scheduled_events(self, event_type):
        """Removes all scheduled events of a specific type for this entity."""
        self.environment.clear_events(self.entity_id, event_type)

    def schedule_event(self, event):
        simulation_event = SimulationEvent(
            time=event['time'],
            entity=self,
            event_type=event['type'],
            params=event['params']
        )
        self.environment.schedule_event(simulation_event)
        logging.info(f"Scheduled event at time {event['time']} for entity {self.entity_id}")