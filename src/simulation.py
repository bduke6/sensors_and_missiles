import os
import datetime
import logging.config
import yaml
from environment import Environment
from entity import Entity
from logging_config import SimulationTimeFilter
import sys
import json

def clear_logs_directory(log_dir):
    """Delete all files in the logs directory."""
    for filename in os.listdir(log_dir):
        file_path = os.path.join(log_dir, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Deleted old log file: {file_path}")
        except OSError as e:
            print(f"Error deleting {file_path}: {e}")

def setup_logging(config, env):
    logging_config_path = config['environment']['logging_config']
    with open(logging_config_path, 'r') as f:
        logging_config = yaml.safe_load(f)

    # Clear the logs directory before setting up new logs
    logs_dir = 'logs'
    clear_logs_directory(logs_dir)

    # Create a datetime string to append to filenames
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    # Update log filenames with the timestamp
    for handler in logging_config.get('handlers', {}).values():
        if 'filename' in handler:
            base_name = os.path.basename(handler['filename'])
            handler['filename'] = os.path.join(logs_dir, f"{timestamp}_{base_name}")

    # Initialize logging with the updated configuration
    logging.config.dictConfig(logging_config)

    # Write CSV header for map data if required
    map_log_path = os.path.join(logs_dir, f"{timestamp}_map_data.csv")
    with open(map_log_path, 'w') as map_log_file:
        map_log_file.write("time,entity,lat,lon,heading,alt\n")

    # Apply the SimulationTimeFilter
    simulation_time_filter = SimulationTimeFilter(env)
    for handler in logging.getLogger().handlers:
        handler.addFilter(simulation_time_filter)

    # Ensure filter is also applied to map_logger
    map_logger = logging.getLogger('map_logger')
    for handler in map_logger.handlers:
        handler.addFilter(simulation_time_filter)

    print(f"Logging initialized. Log files created with timestamp {timestamp}")

def run_simulation(config_path):
    """Run the simulation."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    env = Environment()
    setup_logging(config, env)

    # Extract entities and scenario files from config
    entities_file = config['environment']['entities_file']
    scenario_file = config['environment']['scenario_file']
    max_time = config['environment']['max_time']

    logging.info(f"Starting simulation with config: {config_path}")
    logging.info(f"Entities file: {entities_file}")
    logging.info(f"Scenario file: {scenario_file}")

    # Load entities from JSON file
    with open(entities_file, 'r') as f:
        entities_config = json.load(f)

    for entity_config in entities_config['entities']:
        entity = Entity(entity_config, env)
        env.add_entity(entity)
        logging.info(f"Added entity: {entity.entity_id}")

    logging.info("Starting event processing")
    env.process_events(max_time)
    logging.info("Simulation completed successfully.")

if __name__ == "__main__":
    config_path = sys.argv[1]
    run_simulation(config_path)
