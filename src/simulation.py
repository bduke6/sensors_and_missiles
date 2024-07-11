import argparse
import numpy as np
import matplotlib.pyplot as plt
from src.entities import Missile, Ship, Aircraft
from src.sensors import Sensor
from src.environment import Environment
from src.events import LaunchEvent
from src.config import Config

# Set up argument parsing
parser = argparse.ArgumentParser(description='Run the simulation with the specified configuration file.')
parser.add_argument('config_file', type=str, help='Path to the configuration file')

args = parser.parse_args()

# Load configuration
config = Config(args.config_file)

# Initialize environment
env = Environment()

# Add entities
missile = Missile(position=config.get('entities.missile.position'), velocity=config.get('entities.missile.velocity'))
ship = Ship(position=config.get('entities.ship.position'), velocity=config.get('entities.ship.velocity'))
aircraft = Aircraft(position=config.get('entities.aircraft.position'), velocity=config.get('entities.aircraft.velocity'))

env.add_entity(missile)
env.add_entity(ship)
env.add_entity(aircraft)

# Add sensors
for sensor_config in config.get('sensors'):
    sensor = Sensor(location=sensor_config['location'], range=sensor_config['range'])
    env.add_sensor(sensor)

# Schedule initial events
env.schedule_event(LaunchEvent(0, missile, None))

# Run simulation
env.process_events(max_time=config.get('environment.max_time'))

# Visualization
if config.get_bool('environment.display_plot', False):
    positions = {entity: [] for entity in env.entities}

    for entity in env.entities:
        positions[entity].append(entity.position.copy())

    for entity, pos_list in positions.items():
        pos_array = np.array(pos_list)
        plt.plot(pos_array[:, 0], pos_array[:, 1], label=f'{type(entity).__name__} Trajectory')

    for sensor in env.sensors:
        circle = plt.Circle(sensor.location.coords[0], sensor.range, color='r', fill=False, label='Sensor Range')
        plt.gca().add_patch(circle)

    plt.xlabel('X Position (m)')
    plt.ylabel('Y Position (m)')
    plt.legend()
    plt.show()
