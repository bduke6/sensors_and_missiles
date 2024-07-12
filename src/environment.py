import logging
import heapq

class Environment:
    def __init__(self):
        self.entities = []
        self.sensors = []
        self.events = []
        self.current_time = 0
        self.logger = logging.getLogger("environment")
        self.event_queue = []

    def add_entity(self, entity):
        self.entities.append(entity)
        self.logger.info(f"Added entity: {entity}")

    def add_sensor(self, sensor):
        self.sensors.append(sensor)
        self.logger.info(f"Added sensor: {sensor}")

    def schedule_event(self, event):
        heapq.heappush(self.event_queue, event)
        self.logger.info(f"Scheduled event: {event}")

    def process_events(self, max_time):
        while self.current_time < max_time:
            if not self.event_queue:
                break
            event = heapq.heappop(self.event_queue)
            self.current_time = event.time
            self.logger.info(f"Handling event: {event} at time {self.current_time}")
            event.handle()

    def update_environment(self, time):
        self.logger.debug(f"Updating environment at time {time}")
        for entity in self.entities:
            entity.update(time)
