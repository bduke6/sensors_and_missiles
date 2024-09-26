import logging
import logging.config  # Ensure proper logging configuration
import yaml
import json
import os
import sys
from environment import Environment
from entity import Entity
from logging_config import SimulationTimeFilter

def remove_old_logs(log_files):
    """Function to remove old log files."""
    if isinstance(log_files, str):
        log_files = [log_files]
    for log_file in log_files:
        try:
            if os.path.isfile(log_file):
                os.remove(log_file)
                print(f"Removed old log file: {log_file}")
        except OSError as e:
            print(f"Error removing {log_file}: {e}")
            

def setup_logging(config, env):
    logging_config_path = config['environment']['logging_config']
    with open(logging_config_path, 'r') as f:
        logging_config = yaml.safe_load(f)

    # Initialize logging
    log_files = [handler['filename'] for handler in logging_config.get('handlers', {}).values() if 'filename' in handler]
    remove_old_logs(log_files)
    logging.config.dictConfig(logging_config)

    # Manually write the CSV header to map_data.csv
    with open('logs/map_data.csv', 'w') as map_log_file:
        map_log_file.write("sim_time,entity_id,lat,lon,heading\n")


    # Simulation time filter to sync time with events
    simulation_time_filter = SimulationTimeFilter(env)
    for handler in logging.getLogger().handlers:
        handler.addFilter(simulation_time_filter)

    # Ensure the filter is added to map_logger as well
    map_logger = logging.getLogger('map_logger')
    for handler in map_logger.handlers:
        handler.addFilter(simulation_time_filter)

def run_simulation(config_path):
    """Run the simulation."""
    # Load the simulation configuration
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Initialize the environment instance before logging setup
    env = Environment()

    # Set up logging with environment passed for SimulationTimeFilter
    setup_logging(config, env)

    # Extract entities and scenario files from the config
    entities_file = config['environment']['entities_file']
    scenario_file = config['environment']['scenario_file']
    max_time = config['environment']['max_time']

    logging.info(f"Starting simulation with config: {config_path}")
    logging.info(f"Entities file: {entities_file}")
    logging.info(f"Scenario file: {scenario_file}")

    # Load entities from JSON file
    with open(entities_file, 'r') as f:
        entities_config = json.load(f)

    # Iterate over entities in the entities_config list and create them
    for entity_config in entities_config['entities']:
        entity = Entity(entity_config, env)  # Pass environment to Entity
        env.add_entity(entity)  # Add entity to the environment
        logging.info(f"Added entity: {entity.entity_id}")

    # Process events based on the scenario file
    logging.info("Starting event processing")
    env.process_events(max_time)  # Process events in the environment
    logging.info("Simulation completed successfully.")

if __name__ == "__main__":
    # Run the simulation with the config path provided in the command line arguments
    config_path = sys.argv[1]
    run_simulation(config_path)