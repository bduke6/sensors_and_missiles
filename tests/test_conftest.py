import pytest
import yaml
import json
import os

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
                {"lat": 0, "lon": 0, "alt": 0, "velocity": [1, 1, 1], "orientation": [1, 0, 0], "id": "missile_1"}
            ],
            "ships": [
                {"lat": 0, "lon": 0, "alt": 0, "velocity": [0, 0, 0], "orientation": [1, 0, 0], "id": "ship_1"}
            ],
            "aircrafts": [
                {"lat": 0, "lon": 0, "alt": 0, "velocity": [1, 1, 1], "orientation": [1, 0, 0], "id": "aircraft_1"}
            ]
        }
    }

    scenario_config_data = {
        "events": [
            {"type": "TimingEvent", "time": 5, "action": {"type": "launch_missile", "params": {"missile_id": "missile_1", "target_id": "ship_1"}}}
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
