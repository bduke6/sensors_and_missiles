import numpy as np
from src.events import LaunchEvent  # Ensure this import is present

class Entity:
    def __init__(self, position, velocity):
        self.position = np.array(position)
        self.velocity = np.array(velocity)
    
    def update_position(self, dt):
        self.position += self.velocity * dt
    
    def launch_missile(self, target, env, time):
        missile = Missile(self.position.copy(), np.array([100, 0, 100]))  # Example velocity
        env.add_entity(missile)
        env.schedule_event(LaunchEvent(time, missile, target))

class Missile(Entity):
    def __init__(self, position, velocity):
        super().__init__(position, velocity)
        # Additional attributes specific to missiles

class Ship(Entity):
    def __init__(self, position, velocity):
        super().__init__(position, velocity)
        # Additional attributes specific to ships

class Aircraft(Entity):
    def __init__(self, position, velocity):
        super().__init__(position, velocity)
        # Additional attributes specific to aircraft
