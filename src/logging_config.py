# logging_config.py
import logging
import yaml
import os

import logging

class SimulationTimeFilter(logging.Filter):
    def __init__(self, env):
        self.env = env
        super().__init__()

    def filter(self, record):
        # Set a default value for simulation_time if it's not available
        record.simulation_time = round(getattr(self.env, 'current_time', 0), 2)
        return True

import os
import logging
from datetime import datetime

class FileHandlerWithHeader(logging.FileHandler):
    def __init__(self, filename, mode='a', header=None, **kwargs):
        super().__init__(filename, mode, **kwargs)
        
        # Generate the current date and time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Prepare the header with date and time
        if header:
            full_header = f"=== Log Start ===\nDate and Time: {current_time}\n{header}\n"
        else:
            full_header = f"=== Log Start ===\nDate and Time: {current_time}\n"
        
        # Append the header to the file every time it is opened
        with open(filename, 'a') as log_file:
            log_file.write(full_header)


# Function to set up the logger
def setup_logging(env):
    with open('path/to/logging.yaml', 'r') as f:
        config = yaml.safe_load(f)
        logging.config.dictConfig(config)

    # Apply the simulation time filter to all loggers
    simulation_time_filter = SimulationTimeFilter(env)
    logging.getLogger().addFilter(simulation_time_filter)

    # Manually add FileHandlerWithHeader to the root logger
    header = "=== Log Start ===\nTimestamp - Logger Name - Log Level - Message"
    file_handler_with_header = FileHandlerWithHeader('logs/simulation.log', mode='w', header=header)
    logging.getLogger().addHandler(file_handler_with_header)

