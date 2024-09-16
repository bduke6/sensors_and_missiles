import json
import yaml
import logging
import logging.config
import os  # Import os to handle file deletion
from environment import Environment
from entities import Ship, Missile, Aircraft
from events import LaunchEvent
from logging_config import SimulationTimeFilter, FileHandlerWithHeader


import os
import logging

import os
import logging

def remove_old_logs(log_files):
    """Remove old log files if they exist."""
    if isinstance(log_files, str):  # If a single string is passed, convert it to a list
        log_files = [log_files]
        
    for log_file in log_files:
        try:
            log_file = log_file.strip()  # Strip any unnecessary whitespace
            if os.path.isfile(log_file):  # Ensure we are dealing with files, not directories
                os.remove(log_file)
                print(f"Removed old log file: {log_file}")
            else:
                print(f"Log file {log_file} does not exist or is not a file.")
        except OSError as e:
            print(f"Error removing {log_file}: {e}")

# Continue with your simulation setup and logging configuration
logging.basicConfig(level=logging.INFO)
logging.info("Starting simulation...")

def setup_logging(config, env):
    logging_config_path = config['environment']['logging_config']
    with open(logging_config_path, 'r') as f:
        logging_config = yaml.safe_load(f)

    # Collect all log file paths into a list
    log_files = []
    for handler in logging_config.get('handlers', {}).values():
        if 'filename' in handler:
            log_file_path = handler['filename']
            log_files.append(log_file_path)

    # Remove old logs by passing the correct list of log files
    remove_old_logs(log_files)

    logging.config.dictConfig(logging_config)

    # Apply the simulation time filter to all loggers' handlers
    simulation_time_filter = SimulationTimeFilter(env)
    for handler in logging.getLogger().handlers:
        handler.addFilter(simulation_time_filter)

    # Add the filter to all named loggers as well
    for logger_name in logging.root.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        for handler in logger.handlers:
            handler.addFilter(simulation_time_filter)

def run_simulation(config_path):
    # Load the simulation configuration
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Initialize the environment instance before logging setup
    env = Environment()

    # Set up logging with environment passed for SimulationTimeFilter
    setup_logging(config, env)

    entities_file = config['environment']['entities_file']
    scenario_file = config['environment']['scenario_file']
    max_time = config['environment']['max_time']

    logging.info(f"Starting simulation with config: {config_path}")
    logging.info(f"Entities file: {entities_file}")
    logging.info(f"Scenario file: {scenario_file}")

    # Load entities from JSON file
    with open(entities_file, 'r') as f:
        entities_config = json.load(f)

    # Load scenario from YAML file
    with open(scenario_file, 'r') as f:
        scenario_config = yaml.safe_load(f)

    entities = {}

    # Add ships and missiles, ensuring each has a unique UID
    for ship_config in entities_config['entities'].get('ships', []):
        ship = Ship(lat=ship_config['lat'], lon=ship_config['lon'], alt=ship_config['alt'],
                    velocity=ship_config['velocity'], orientation=ship_config['orientation'], 
                    entity_id=ship_config['entity_id'])
        env.add_entity(ship)
        entities[ship.entity_id] = ship
        logging.info(f"Added ship: {ship.entity_id}")

        # Add missiles from armaments
        for armament in ship_config.get('armaments', []):
            for missile_config in armament.get('missiles', []):
                missile = Missile(lat=missile_config['lat'], lon=missile_config['lon'], alt=missile_config['alt'],
                                  velocity=missile_config['velocity'], orientation=[75, 0, 0],  # Change to 75 degrees
                                  fuel=missile_config['fuel'], entity_id=missile_config['entity_id'])
                env.add_entity(missile)
                entities[missile.entity_id] = missile
                logging.info(f"Added missile: {missile.entity_id}")

    # Add aircrafts if needed
    for aircraft_config in entities_config['entities'].get('aircrafts', []):
        aircraft = Aircraft(lat=aircraft_config['lat'], lon=aircraft_config['lon'], alt=aircraft_config['alt'],
                            velocity=aircraft_config['velocity'], orientation=aircraft_config['orientation'],
                            entity_id=aircraft_config['entity_id'])
        env.add_entity(aircraft)
        entities[aircraft.entity_id] = aircraft
        logging.info(f"Added aircraft: {aircraft.entity_id}")

        # Add missiles not embedded in ships
    # Modify missile initialization to use config values
    for missile_config in entities_config['entities'].get('missiles', []):
        print(f"Missile fuel in config: {missile_config.get('fuel', 100)}")
        
        missile = Missile(
            lat=missile_config['lat'],
            lon=missile_config['lon'],
            alt=missile_config['alt'],
            velocity=missile_config.get('velocity', [0, 0, 0]),  # Default velocity if not specified
            orientation=missile_config.get('orientation', [90, 0, 0]),  # Default orientation if not specified
            fuel=missile_config.get('fuel', 100),  # Default fuel if not specified
            entity_id=missile_config['entity_id']
        )
        env.add_entity(missile)
        entities[missile.entity_id] = missile
        logging.info(f"Added missile: {missile.entity_id}")

    # Schedule events like missile launches
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