import logging
import heapq

class Environment:
    def __init__(self):
        self.entities = []
        self.sensors = []
        self.events = []
        self.current_time = 0  # Initialize current_time here
        self.logger = logging.getLogger("environment")
        self.event_queue = []

    def add_entity(self, entity):
        self.entities.append(entity)
        self.logger.info(f"Added entity: {entity}")

    def schedule_event(self, event):
        heapq.heappush(self.event_queue, event)
        self.logger.info(f"Scheduled event: {event}")

    def process_events(self, max_time):
        self.max_time = max_time
        self.time_step = 1  # default time_step
        while self.current_time < max_time:
            if not self.event_queue:
                break
            event = heapq.heappop(self.event_queue)
            self.current_time = event.time  # Ensure this is set correctly
            self.logger.info(f"Handling event: {event} at time {self.current_time}")
            event.process(self)

    def update_environment(self, time):
        self.logger.debug(f"Updating environment at time {time}")
        for entity in self.entities:
            entity.update(time)
