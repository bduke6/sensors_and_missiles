import uuid
import logging
from entities import Missile, Ship

class Event:
    def __init__(self, time):
        self.time = time
        self.event_id = uuid.uuid4()

    def process(self, environment):
        raise NotImplementedError("This method should be implemented by subclasses.")

class LaunchEvent(Event):
    def __init__(self, time, missile, target):
        super().__init__(time)
        self.missile = missile
        self.target = target
        self.logger = logging.getLogger("root")

    def process(self, environment):
        self.logger.info(f"Processing LaunchEvent: {self.event_id} for missile {self.missile.entity_id}")
        self.missile.launch(self.target, environment)  # Pass the environment


class MovementEvent(Event):
    def __init__(self, time, entity):
        super().__init__(time)
        self.entity = entity
        self.logger = logging.getLogger("root")

    def process(self, environment):
        time_step = 0.1  # You can adjust the time step if necessary
        self.entity.move(time_step)
        self.logger.info(f"Entity {self.entity.entity_id} moved to lat: {self.entity.lat}, lon: {self.entity.lon}, alt: {self.entity.alt}")

        # If the entity is a missile, check if it still has fuel or is above a certain altitude
        if isinstance(self.entity, Missile) and self.entity.fuel > 0:
            next_event_time = self.time + time_step
            next_event = MovementEvent(next_event_time, self.entity)
            environment.schedule_event(next_event)
        elif isinstance(self.entity, Ship):
            # Ships continue moving without fuel limitations, for example
            next_event_time = self.time + time_step
            next_event = MovementEvent(next_event_time, self.entity)
            environment.schedule_event(next_event)
