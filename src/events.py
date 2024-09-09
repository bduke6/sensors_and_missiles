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
        # Move the entity and let the entity decide whether to schedule more events
        time_step = 0.1  # You can adjust the time step
        self.entity.move(time_step, environment)



