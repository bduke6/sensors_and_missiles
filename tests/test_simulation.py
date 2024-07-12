import os
import sys
import pytest
import json
import yaml
from simulation import run_simulation

# Ensure the src directory is in the PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

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
            "missiles": [
                {"lat": 0, "lon": 0, "alt": 0, "velocity": [100, 0, 100], "orientation": [1, 0, 0], "entity_id": "missile_1"}
            ],
            "ships": [
                {"lat": -500, "lon": 0, "alt": 0, "velocity": [10, 0, 0], "orientation": [1, 0, 0], "entity_id": "ship_1",
                 "sensors": [{"lat": -500, "lon": 0, "alt": 0, "range": 1000}],
                 "armaments": [{"missiles": [{"lat": -500, "lon": 0, "alt": 0, "velocity": [100, 0, 100], "orientation": [1, 0, 0], "entity_id": "missile_2"}]}]
                }
            ],
            "aircrafts": [
                {"lat": 0, "lon": 1000, "alt": 1000, "velocity": [200, 0, 0], "orientation": [1, 0, 0], "entity_id": "aircraft_1",
                 "sensors": [{"lat": 0, "lon": 1000, "alt": 1000, "range": 1500}],
                 "armaments": [{"missiles": [{"lat": 0, "lon": 1000, "alt": 1000, "velocity": [100, 0, 100], "orientation": [1, 0, 0], "entity_id": "missile_3"}]}]
                }
            ]
        }
    }

    scenario_config_data = {
        "events": [
            {
                "type": "TimingEvent",
                "time": 5,
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

def test_simulation_run(temp_config_files):
    run_simulation(temp_config_files)
    # Assertions to verify the simulation run can be added here
