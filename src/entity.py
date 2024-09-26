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
        self.velocity_vector_ecef = None  # ECEF velocity vector managed by navigator
        logging.info(f"Entity created: {self.entity_id}")

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
        """Process communication events."""
        message_type = params.get('message_type', None)
        
        # Handle navigation message
        if message_type == 'nav':
            logging.info(f"Received navigation message for {self.entity_id}")
            self.navigator(params)
        else:
            logging.info(f"Unknown message type for {self.entity_id}: {message_type}")

    def navigator(self, params):
        """Navigator calculates and stores the ECEF velocity vector."""
        heading = params['heading']
        speed = params['speed']
        altitude = params.get('altitude', self.alt)  # Default to current altitude if not specified
        dt = 1  # Time step

        # Calculate ECEF velocity vector based on heading, speed, and time step
        slant_range_per_sec = speed * dt
        # Calculate azimuth and use aer2enu to get relative motion in East/North/Up
        new_e, new_n, new_u = pm.aer2enu(heading, 0, slant_range_per_sec)
        
        # Convert this ENU vector to an ECEF velocity vector (this will be used by the mover)
        velocity_vector_ecef = pm.enu2ecef_vector(new_e, new_n, new_u, self.lat, self.lon, altitude)
        
        # Store the ECEF velocity vector in the entity
        self.velocity_vector_ecef = velocity_vector_ecef

        # Trigger the mover immediately to apply the velocity vector
        move_event = {
            'type': 'move',
            'time': self.environment.current_time,  # Immediate
            'entity': self
        }
        self.schedule_event(move_event)

        # Schedule a navigator check event to ensure the entity stays on track
        check_event = {
            'type': 'navigator_check',
            'time': self.environment.current_time + 5,  # Check in 5 seconds
            'entity': self
        }
        self.schedule_event(check_event)
        logging.info(f"Scheduled navigation check event at time {self.environment.current_time + 5} for entity {self.entity_id}")

    def move(self):
        """Apply the ECEF velocity vector to update the entity's position."""
        if not self.velocity_vector_ecef:
            logging.warning(f"No velocity vector available for {self.entity_id}, skipping move.")
            return

        velocity_ecef_x, velocity_ecef_y, velocity_ecef_z = self.velocity_vector_ecef
        dt = 1  # Time step

        # Update position in ECEF coordinates by applying the velocity vector
        x_ecef, y_ecef, z_ecef = pm.geodetic2ecef(self.lat, self.lon, self.alt)
        new_x_ecef = x_ecef + velocity_ecef_x * dt
        new_y_ecef = y_ecef + velocity_ecef_y * dt
        new_z_ecef = z_ecef + velocity_ecef_z * dt

        # Convert back to lat/lon/alt
        new_lat, new_lon, new_alt = pm.ecef2geodetic(new_x_ecef, new_y_ecef, new_z_ecef)

        # Update the entity's lat, lon, and altitude
        self.lat, self.lon, self.alt = new_lat, new_lon, new_alt
        logging.info(f"{self.entity_id} moved to {self.lat}, {self.lon} at altitude {self.alt}.")

        # Log the current state to the map data log
        current_time = self.environment.current_time
        self.map_logger.info(f"{current_time},{self.entity_id},{self.lat:.6f},{self.lon:.6f},{self.alt:.6f}")

        # Schedule the next move event (continue applying the velocity vector)
        next_move_event = {
            'type': 'move',
            'time': current_time + dt,  # Continue moving in the next time step
            'entity': self
        }
        self.schedule_event(next_move_event)
        logging.info(f"Scheduled next move event at time {current_time + dt} for entity {self.entity_id}")

    def navigator_check(self):
        """Check if the entity is still on track or needs adjustments."""
        logging.info(f"Navigator checking course for {self.entity_id}.")
        # Later, this function could check for course corrections or stop commands.
        
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