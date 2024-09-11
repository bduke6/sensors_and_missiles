import uuid
import logging

# Create a logger for events
event_logger = logging.getLogger('event')

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

    def process(self, environment):
        event_logger.info(f"Processing LaunchEvent: {self.event_id} for missile {self.missile.entity_id}")
        self.missile.launch(self.target, environment)  # Let the missile handle its launch and scheduling

class MovementEvent(Event):
    def __init__(self, time, entity, time_step):
        super().__init__(time)
        self.entity = entity
        self.time_step = time_step  # Include time step in the event

    def process(self, environment):
        event_logger.info(f"Processing MovementEvent: {self.event_id} for entity {self.entity.entity_id}")
        # Let the entity handle its movement and whether it schedules another event
        self.entity.handle_event(self, environment)
