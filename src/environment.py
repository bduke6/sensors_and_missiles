import heapq
import logging
from simulation_event import SimulationEvent

import heapq
import logging

class Environment:
    def __init__(self):
        self.entities = []
        self.event_queue = []
        self.current_time = 0  # Initialize current_time to track the simulation's time
        self.logger = logging.getLogger("environment")
    
    def add_entity(self, entity):
        self.entities.append(entity)
        self.logger.info(f"Added entity: {entity.entity_id}")

    def schedule_event(self, simulation_event):
        """Schedule the event in the event queue based on time."""
        heapq.heappush(self.event_queue, simulation_event)
        self.logger.info(f"Scheduled event: {simulation_event} at time {simulation_event.time}")
    
    def process_events(self, max_time):
        """Process events from the event queue."""
        while self.event_queue and self.current_time < max_time:
            simulation_event = heapq.heappop(self.event_queue)
            self.current_time = simulation_event.time  # Update current_time to the event's time
            self.logger.info(f"Processing event for {simulation_event.entity.entity_id} at time {self.current_time}: {simulation_event}")
            simulation_event.entity.process_event({
                'type': simulation_event.event_type,
                'params': simulation_event.params
            })