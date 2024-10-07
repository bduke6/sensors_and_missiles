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
        self.velocity_vector_ecef = None  # ECEF velocity vector set by navigator
        logging.info(f"Entity created: {self.entity_id}")

        # Initialize ECEF position based on the initial geodetic coordinates
        self.ecef_x, self.ecef_y, self.ecef_z = pm.geodetic2ecef(self.lat, self.lon, self.alt)
        logging.info(f"{self.entity_id} initial ECEF Position: x={self.ecef_x}, y={self.ecef_y}, z={self.ecef_z}")

        # Schedule the first communication event from the config
        if self.events:
            first_event = {
                'type': self.events[0]['type'],
                'time': self.events[0]['start_time'],
                'entity': self,
                'params': self.events[0]['params']
            }
            self.schedule_event(first_event)

    def process_event(self, event):
        logging.info(f"Processing event for {self.entity_id}: {event}")
        if event['type'] == 'commo':
            self.commo(event['params'])
        elif event['type'] == 'move':
            self.move()
        elif event['type'] == 'navigator_check':
            self.navigator_check()

    def commo(self, params):
        """Process communication events to handle navigation messages."""
        message_type = params.get('message_type', None)
        
        if message_type == 'nav':
            logging.info(f"Received navigation message for {self.entity_id}")
            self.navigator(params)
        else:
            logging.info(f"Unknown message type for {self.entity_id}: {message_type}")

    def navigator(self, params):
        """Navigator function to calculate and set the initial ECEF velocity vector."""
        self.heading = params['heading']
        self.speed = params['speed']
        self.alt = params.get('altitude', self.alt)  # Default to current altitude if not specified
        dt = 1  # Time step in seconds

        # Calculate ENU velocity components from heading and speed for flat trajectory
        slant_range_per_sec = self.speed * dt
        east, north, up = pm.aer2enu(self.heading, 0, slant_range_per_sec, deg=True)

        # Convert ENU velocity to ECEF velocity based on current position
        x_ecef_vel, y_ecef_vel, z_ecef_vel = pm.enu2ecef(east, north, up, self.lat, self.lon, self.alt, deg=True)

        # Store the ECEF velocity vector
        self.velocity_vector_ecef = (x_ecef_vel - self.ecef_x, y_ecef_vel - self.ecef_y, z_ecef_vel - self.ecef_z)
        
        # Schedule the initial move event
        next_event = {
            'type': 'move',
            'time': self.environment.current_time + dt,
            'entity': self,
            'params': {
                'velocity_vector': self.velocity_vector_ecef,
                'altitude': self.alt,
            }
        }
        self.schedule_event(next_event)
        logging.info(f"Navigator set initial velocity vector: {self.velocity_vector_ecef}")

    def move(self):
        """Apply the ECEF velocity vector to update the entity's position while maintaining altitude."""
        if not self.velocity_vector_ecef:
            logging.warning(f"No velocity vector available for {self.entity_id}, skipping move.")
            return

        dt = 1  # Time step in seconds

        # Current ECEF position
        x_ecef, y_ecef, z_ecef = pm.geodetic2ecef(self.lat, self.lon, self.alt)
        logging.debug(f"{self.entity_id} ECEF Position before move: x={x_ecef}, y={y_ecef}, z={z_ecef}")

        # Apply ECEF velocity vector to update position
        new_x_ecef = x_ecef + self.velocity_vector_ecef[0] * dt
        new_y_ecef = y_ecef + self.velocity_vector_ecef[1] * dt
        new_z_ecef = z_ecef + self.velocity_vector_ecef[2] * dt
        logging.debug(f"{self.entity_id} ECEF Position after move: x={new_x_ecef}, y={new_y_ecef}, z={new_z_ecef}")
        

        # Convert updated ECEF coordinates back to geodetic (lat, lon)
        new_lat, new_lon, new_alt = pm.ecef2geodetic(new_x_ecef, new_y_ecef, new_z_ecef)
        logging.debug(f"{self.entity_id} Geodetic Position after move: lat={new_lat}, lon={new_lon}, alt={new_alt}")

        # Maintain altitude by enforcing the specified altitude
        self.lat, self.lon, self.alt = new_lat, new_lon, new_alt
        logging.info(f"{self.entity_id} moved to {self.lat}, {self.lon} at altitude {self.alt}")

        # Log current state to map data log
        current_time = self.environment.current_time
        self.map_logger.info(f"{current_time},{self.entity_id},{self.lat:.6f},{self.lon:.6f},{self.heading:.6f},{self.alt:.6f}")

        # Schedule the next move event to maintain movement
        next_move_event = {
            'type': 'move',
            'time': current_time + dt,
            'entity': self,
            'params': {'velocity_vector': self.velocity_vector_ecef, 'altitude': self.alt}
        }
        self.schedule_event(next_move_event)
        logging.info(f"Scheduled next move event at time {current_time + dt} for entity {self.entity_id}")

    def navigator_check(self):
        """Check if the entity's heading and altitude deviate from the target values."""
        logging.info(f"Navigator checking course for {self.entity_id}.")
        
        # Get the current heading and altitude based on the navigator's instruments
        current_lat, current_lon, current_alt = self.lat, self.lon, self.alt
        # Calculate current bearing (heading) based on previous position (stored ECEF)
        x_ecef, y_ecef, z_ecef = pm.geodetic2ecef(current_lat, current_lon, current_alt)
        current_heading = self.heading  # or calculated from past data if using a simulated compass

        # Check for deviation in heading and altitude
        heading_deviation = abs(current_heading - self.heading) / self.heading * 100
        altitude_deviation = abs(current_alt - self.alt) / self.alt * 100

        if heading_deviation > 10 or altitude_deviation > 10:
            logging.info(f"{self.entity_id} off course: heading deviation = {heading_deviation:.2f}%, altitude deviation = {altitude_deviation:.2f}%")
            
            # Adjust velocity vector to correct course and altitude
            self.navigator({'heading': self.heading, 'speed': self.speed, 'altitude': self.alt})
        
        # Schedule the next navigator check
        next_check_event = {
            'type': 'navigator_check',
            'time': self.environment.current_time + 5,  # Check again in 5 seconds
            'entity': self
        }
        self.schedule_event(next_check_event)
        logging.info(f"Scheduled next navigator check at time {self.environment.current_time + 5} for entity {self.entity_id}")


    def schedule_event(self, event):
        """Schedule an event in the environment."""
        simulation_event = SimulationEvent(
            time=event['time'],
            entity=self,
            event_type=event['type'],
            params=event['params']
        )
        self.environment.schedule_event(simulation_event)
        logging.info(f"Scheduled event at time {event['time']} for entity {self.entity_id}")
