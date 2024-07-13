import json
import yaml
import logging
import logging.config
from environment import Environment
from entities import Ship, Missile, Aircraft
from events import LaunchEvent

def setup_logging(config):
    logging_config = config['environment']['logging_config']
    with open(logging_config, 'r') as f:
        logging.config.dictConfig(yaml.safe_load(f))

def run_simulation(config_path):
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    setup_logging(config)

    entities_file = config['environment']['entities_file']
    scenario_file = config['environment']['scenario_file']
    max_time = config['environment']['max_time']

    logging.info(f"Starting simulation with config: {config_path}")
    logging.info(f"Entities file: {entities_file}")
    logging.info(f"Scenario file: {scenario_file}")

    with open(entities_file, 'r') as f:
        entities_config = json.load(f)

    with open(scenario_file, 'r') as f:
        scenario_config = yaml.safe_load(f)

    env = Environment()
    entities = {}

    # Add ships and extract missiles
    for ship_config in entities_config['entities'].get('ships', []):
        ship = Ship(lat=ship_config['lat'], lon=ship_config['lon'], alt=ship_config['alt'], velocity=ship_config['velocity'], orientation=ship_config['orientation'], entity_id=ship_config['entity_id'])
        env.add_entity(ship)
        entities[ship.entity_id] = ship
        logging.info(f"Added ship: {ship.entity_id}")

        # Extract missiles from armaments
        for armament in ship_config.get('armaments', []):
            for missile_config in armament.get('missiles', []):
                missile = Missile(lat=missile_config['lat'], lon=missile_config['lon'], alt=missile_config['alt'], velocity=missile_config['velocity'], orientation=missile_config['orientation'], entity_id=missile_config['entity_id'])
                env.add_entity(missile)
                entities[missile.entity_id] = missile
                logging.info(f"Added missile: {missile.entity_id}")

    # Add aircrafts
    for aircraft_config in entities_config['entities'].get('aircrafts', []):
        aircraft = Aircraft(lat=aircraft_config['lat'], lon=aircraft_config['lon'], alt=aircraft_config['alt'], velocity=aircraft_config['velocity'], orientation=aircraft_config['orientation'], entity_id=aircraft_config['entity_id'])
        env.add_entity(aircraft)
        entities[aircraft.entity_id] = aircraft
        logging.info(f"Added aircraft: {aircraft.entity_id}")

    # Add missiles not embedded in other entities
    for missile_config in entities_config['entities'].get('missiles', []):
        missile = Missile(lat=missile_config['lat'], lon=missile_config['lon'], alt=missile_config['alt'], velocity=missile_config['velocity'], orientation=missile_config['orientation'], entity_id=missile_config['entity_id'])
        env.add_entity(missile)
        entities[missile.entity_id] = missile
        logging.info(f"Added missile: {missile.entity_id}")

    # Schedule events
    for event_config in scenario_config['events']:
        event_type = event_config['type']
        event_time = event_config['time']
        action = event_config['action']
        if event_type == "TimingEvent" and action['type'] == "launch_missile":
            missile_id = action['params']['missile_id']
            target_id = action['params']['target_id']
            missile = entities[missile_id]
            target = entities[target_id]
            event = LaunchEvent(event_time, missile, target)
            env.schedule_event(event)
            logging.info(f"Scheduled event: {event}")

    logging.info("Starting event processing")
    env.process_events(max_time)
    logging.info("Simulation completed successfully.")


if __name__ == "__main__":
    import sys
    config_path = sys.argv[1]
    run_simulation(config_path)
