import heapq
import logging

class Environment:
    def __init__(self):
        self.event_queue = []  # Event priority queue
        self.current_time = 0  # Start time of the simulation
        self.entities = []  # List to store entities in the environment

    def add_entity(self, entity):
        """Add an entity to the environment."""
        self.entities.append(entity)
        logging.info(f"Entity {entity.entity_id} added to the environment.")

    def schedule_event(self, simulation_event):
        """Schedule an event in the environment."""
        heapq.heappush(self.event_queue, (simulation_event.time, simulation_event))
        logging.info(f"Event scheduled at time {simulation_event.time} for {simulation_event.entity.entity_id}")

    def process_events(self, max_time):
        """Process all events until max_time is reached or no events are left."""
        while self.event_queue and self.current_time < max_time:
            # Get the next event in the queue
            event_time, simulation_event = heapq.heappop(self.event_queue)
            self.current_time = event_time  # Move time forward to the event time

            # Log event queue size
            logging.info(f"Event queue size: {len(self.event_queue)}")

            # Process the event by passing relevant data, ensure 'params' exists
            simulation_event.entity.process_event({
                'type': simulation_event.event_type,
                'time': simulation_event.time,
                'params': simulation_event.params or {}  # Default to empty dict if None
            })

            # Log processing of the event
            logging.info(f"Processed event for {simulation_event.entity.entity_id} at time {self.current_time}")

        logging.info(f"Event processing completed at time {self.current_time}")
