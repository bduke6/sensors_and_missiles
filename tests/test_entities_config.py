import json
import yaml
import logging
import logging.config
from environment import Environment
from entities import Ship
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
    print(f"Entities file path: {entities_file}")  # Debug print
    print(f"Scenario file path: {scenario_file}")  # Debug print

    with open(entities_file, 'r') as f:
        entities_config = json.load(f)

    with open(scenario_file, 'r') as f:
        scenario_config = yaml.safe_load(f)

    env = Environment()
    entities = {}

    # Add entities
    print(f"Entities config: {entities_config}")  # Debug print
    for ship_config in entities_config['entities']['ships']:
        print(f"Processing ship config: {ship_config}")  # Debug print
        ship = Ship(lat=ship_config['lat'], lon=ship_config['lon'], alt=ship_config['alt'], velocity=ship_config['velocity'], orientation=ship_config['orientation'], entity_id=ship_config['id'])
        env.add_entity(ship)
        entities[ship.id] = ship

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
            event = LaunchEvent(time=event_time, entity=missile, target=target)
            env.schedule_event(event)

    env.process_events(max_time=config['environment']['max_time'])
