import pymap3d as pm
import logging
from ballistic_navigator import BallisticNavigator  # Import the ballistic navigator class

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
        self.heading = 0  # Initialize heading to 0 or any default value

        # New attribute to determine if this is a ballistic entity
        self.is_ballistic = config.get('is_ballistic', False)  # Default to False if not specified

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
        message_type = event['type']
        params = event['params']

        if message_type == 'move':
            self.move()
        elif message_type == 'navigator_check':
            self.navigator_check()
        else:
            self.commo(message_type, params)

    def commo(self, message_type, params):
        if message_type == 'nav':
            logging.info(f"Received navigation message for {self.entity_id}")
            self.navigator(params)
        elif message_type == 'bal_nav':  # Handle ballistic navigation
            logging.info(f"Received ballistic navigation message for {self.entity_id}")
            target_lat = float(params.get('tgt_lat'))
            target_lon = float(params.get('tgt_lon'))
            ballistic_navigator = BallisticNavigator(self, target_lat, target_lon)
            print(f"%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%5tgt_lat: {target_lat} tgt_lon: {target_lon}")
            ballistic_navigator.calculate_ballistic_trajectory()
        else:
            logging.warning(f"Unknown message type '{message_type}' for {self.entity_id}")

    def navigator(self, params):

        try:
            self.target_heading = float(params['heading'])
            self.target_speed = float(params['speed'])
            self.target_altitude = float(params.get('altitude', self.alt))
            self.speed = self.target_speed
            self.heading = self.target_heading
            logging.info(f"Navigator set target heading: {self.target_heading}, speed: {self.target_speed}, altitude: {self.target_altitude} for entity {self.entity_id}")
            logging.info(f"NAVIGATOR received heading: {self.target_heading}, speed: {self.target_speed}, altitude: {self.target_altitude} for entity {self.entity_id}")
        except KeyError as e:
            logging.error(f"Missing parameter in nav command for {self.entity_id}: {e}")
            return

        dt = 1
        x_ecef_vel, y_ecef_vel, z_ecef_vel = pm.aer2ecef(
            az=self.target_heading,
            el=0,
            srange=self.target_speed * dt,
            lat0=self.lat,
            lon0=self.lon,
            alt0=self.alt,
            deg=True
        )

        self.velocity_vector_ecef = (x_ecef_vel - self.ecef_x, y_ecef_vel - self.ecef_y, z_ecef_vel - self.ecef_z)
        self.is_underway = True
        self.underway_time = 1
        self.clear_scheduled_events(event_type='move')

        self.schedule_event({
            'type': 'move',
            'time': self.environment.current_time + dt,
            'entity': self,
            'params': {
                'velocity_vector': self.velocity_vector_ecef,
                'altitude': self.target_altitude
            }
        })
        logging.info(f"Scheduled move event for {self.entity_id} at time {self.environment.current_time + dt}")

        self.schedule_event({
            'type': 'navigator_check',
            'time': self.environment.current_time + dt + 5,
            'entity': self,
            'params': {}
        })
        logging.info(f"Scheduled navigator check for {self.entity_id} at time {self.environment.current_time + dt + 5}")

    def move(self):
        logging.info(f"MOVE function for {self.entity_id} with velocity vector: {self.velocity_vector_ecef} and altitude: {self.alt}")

        if not self.velocity_vector_ecef:
            logging.warning(f"No velocity vector available for {self.entity_id}, skipping move.")
            return

        dt = 1
        self.underway_time += dt
        self.mark_time += dt
        self.ecef_x += self.velocity_vector_ecef[0] * dt
        self.ecef_y += self.velocity_vector_ecef[1] * dt
        self.ecef_z += self.velocity_vector_ecef[2] * dt
        self.lat, self.lon, self.alt = pm.ecef2geodetic(self.ecef_x, self.ecef_y, self.ecef_z)
        heading_str = f"{self.heading:.6f}" if self.heading is not None else "N/A"
        self.map_logger.info(f"{self.environment.current_time},{self.entity_id},{self.lat:.6f},{self.lon:.6f},{heading_str},{self.alt:.6f}")
        logging.debug(f"Altitude after move calculation: {self.alt}")


        if not self.environment.is_event_scheduled('move', self.entity_id, self.environment.current_time + dt):
            self.schedule_event({
                'type': 'move',
                'time': self.environment.current_time + dt,
                'receiver': self.entity_id,
                'params': {
                    'velocity_vector': self.velocity_vector_ecef,
                    'altitude': self.alt
                }
            })
            logging.info(f"Scheduled move event for {self.entity_id} at time {self.environment.current_time + dt}")

    def navigator_check(self):
        logging.info(f"NAVIGATOR CHECK course for {self.entity_id}.")
        
        # Only adjust altitude if the entity is ballistic
        if not self.is_ballistic:
            logging.info(f"{self.entity_id} is not ballistic; skipping altitude adjustment.")
            return

        logging.info(f"Navigator check for {self.entity_id}: Current altitude {self.alt}, Target altitude {self.target_altitude}, Velocity vector: {self.velocity_vector_ecef}")

        target_altitude = self.target_altitude
        altitude_deviation = self.alt - target_altitude
        tolerance_range = 2
        correction_delay = 10 if abs(altitude_deviation) < 10 else 3

        if abs(altitude_deviation) > tolerance_range:
            logging.info(f"{self.entity_id} altitude deviation = {altitude_deviation:.2f}. Adjusting altitude.")
            correction_elevation = -0.1 * (altitude_deviation / abs(altitude_deviation))
            x_ecef_corr, y_ecef_corr, z_ecef_corr = pm.aer2ecef(
                az=self.heading,
                el=correction_elevation,
                srange=self.speed,
                lat0=self.lat,
                lon0=self.lon,
                alt0=self.alt,
                deg=True
            )

            self.velocity_vector_ecef = (
                (x_ecef_corr - self.ecef_x) * 0.5,
                (y_ecef_corr - self.ecef_y) * 0.5,
                (z_ecef_corr - self.ecef_z) * 0.5
            )
            self.clear_scheduled_events(event_type='move')
            self.schedule_event({
                'type': 'move',
                'time': self.environment.current_time + 1,
                'receiver': self.entity_id,
                'params': {'velocity_vector': self.velocity_vector_ecef, 'altitude': target_altitude}
            })
            logging.info(f"Scheduled adjusted move event for {self.entity_id} at time {self.environment.current_time + 1}")

        self.schedule_event({
            'type': 'navigator_check',
            'time': self.environment.current_time + correction_delay,
            'receiver': self.entity_id,
            'params': {}
        })
        logging.info(f"Scheduled next navigator check for {self.entity_id} at time {self.environment.current_time + correction_delay}")

    def clear_scheduled_events(self, event_type):
        self.environment.clear_events(self.entity_id, event_type)

    def schedule_event(self, event):
        self.environment.schedule_event(event)
        logging.info(f"Scheduled event at time {event['time']} for entity {self.entity_id}")
