import pymap3d as pm
import logging
from simulation_event import SimulationEvent

class Entity:
    def __init__(self, config, environment):
        self.entity_id = config['entity_id']
        self.lat = config['lat']
        self.lon = config['lon']
        self.alt = config['alt']
        self.events = config['events']  # Predefined list of events
        self.environment = environment
        logging.info(f"Entity created: {self.entity_id}")

        # Schedule the first event (e.g., move) from the config
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
        if event['type'] == 'move':
            self.move(event['params'])

    def move(self, params):
        logging.info(f"Entity {self.entity_id} is moving with parameters: {params}")
        target_lat = params['target_lat']
        target_lon = params['target_lon']
        speed = params['speed']
        dt = 1  # Time step, adjust if needed

        azimuth, _, slant_range = pm.geodetic2aer(self.lat, self.lon, self.alt, target_lat, target_lon, self.alt)
        slant_range_per_sec = speed * dt
        new_e, new_n, new_u = pm.aer2enu(azimuth, 0, slant_range_per_sec)
        new_lat, new_lon, _ = pm.enu2geodetic(new_e, new_n, new_u, self.lat, self.lon, self.alt)

        self.lat, self.lon = new_lat, new_lon
        logging.info(f"{self.entity_id} moved to {self.lat}, {self.lon} using dead reckoning.")

        # Schedule next move event
        next_move_time = self.environment.current_time + dt
        self.schedule_event({
            'time': next_move_time,
            'type': 'move',
            'params': params
        })

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