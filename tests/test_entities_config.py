import sys
import os
import json
import yaml
import logging
import logging.config
import pytest

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from environment import Environment
from entities import Ship, Missile
from events import LaunchEvent

@pytest.fixture
def temp_config_files():
    config_data = {
        "environment": {
            "max_time": 50,
            "display_plot": False,
            "entities_file": "temp_entities_config.json",
            "scenario_file": "temp_scenario_config.yaml",
            "logging_config": "temp_logging.yaml"
        }
    }

    entities_config_data = {
        "entities": {
            "ships": [
                {
                    "lat": 0, "lon": 0, "alt": 0, "velocity": [0, 0, 0], "orientation": [0, 0, 0], "id": "ship_1",
                    "armaments": [
                        {
                            "missiles": [
                                {"lat": 0, "lon": 0, "alt": 0, "velocity": [0, 0, 0], "orientation": [0, 0, 0], "id": "missile_1"}
                            ]
                        }
                    ]
                }
            ]
        }
    }

    scenario_config_data = {
        "events": [
            {
                "type": "TimingEvent",
                "time": 1,
                "action": {
                    "type": "launch_missile",
                    "params": {
                        "missile_id": "missile_1",
                        "target_id": "ship_1"
                    }
                }
            }
        ]
    }

    logging_config_data = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": "INFO",
                "stream": "ext://sys.stdout"
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"]
        }
    }

    with open('temp_config.yaml', 'w') as f:
        yaml.dump(config_data, f)

    with open('temp_entities_config.json', 'w') as f:
        json.dump(entities_config_data, f)

    with open('temp_scenario_config.yaml', 'w') as f:
        yaml.dump(scenario_config_data, f)

    with open('temp_logging.yaml', 'w') as f:
        yaml.dump(logging_config_data, f)

    yield 'temp_config.yaml'

    os.remove('temp_config.yaml')
    os.remove('temp_entities_config.json')
    os.remove('temp_scenario_config.yaml')
    os.remove('temp_logging.yaml')

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

    with open(entities_file, 'r') as f:
        entities_config = json.load(f)

    with open(scenario_file, 'r') as f:
        scenario_config = yaml.safe_load(f)

    env = Environment()
    entities = {}

    for ship_config in entities_config['entities']['ships']:
        ship = Ship(lat=ship_config['lat'], lon=ship_config['lon'], alt=ship_config['alt'], velocity=ship_config['velocity'], orientation=ship_config['orientation'], entity_id=ship_config['id'])
        env.add_entity(ship)
        entities[ship.entity_id] = ship

        for armament in ship_config['armaments']:
            for missile_config in armament['missiles']:
                missile = Missile(lat=missile_config['lat'], lon=missile_config['lon'], alt=missile_config['alt'], velocity=missile_config['velocity'], orientation=missile_config['orientation'], entity_id=missile_config['id'], fuel=100)
                env.add_entity(missile)
                entities[missile.entity_id] = missile

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

def test_simulation_run(temp_config_files):
    run_simulation(temp_config_files)
    # Assertions to verify the simulation run can be added here
