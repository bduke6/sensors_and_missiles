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

    def is_event_scheduled(self, event_type, entity_id, time):
        """Check if an event of a specific type is scheduled for an entity at a given time."""
        for event_time, event in self.event_queue:
            if event_time == time and event.entity.entity_id == entity_id and event.event_type == event_type:
                return True
        return False

    def clear_events(self, entity_id, event_type):
        """Remove all events of a specific type for a given entity from the event queue."""
        # Filter events that don't match the criteria
        self.event_queue = [(time, event) for time, event in self.event_queue 
                            if not (event.entity.entity_id == entity_id and event.event_type == event_type)]
        
        # Re-heapify the event queue to maintain heap properties
        heapq.heapify(self.event_queue)
        logging.info(f"Cleared all '{event_type}' events for entity {entity_id}.")

    def process_events(self, max_time):
        """Process all events until max_time is reached or no events are left."""
        while self.event_queue and self.current_time < max_time:
            # Get the next event in the queue
            event_time, simulation_event = heapq.heappop(self.event_queue)
            self.current_time = event_time  # Move time forward to the event time

            # Log event queue size
            logging.info(f"Event queue size: {len(self.event_queue)}")

            # Process the event by passing relevant data
            simulation_event.entity.process_event({
                'type': simulation_event.event_type,
                'time': simulation_event.time,
                'params': simulation_event.params or {}  # Default to empty dict if None
            })

            # Log processing of the event
            logging.info(f"Processed event for {simulation_event.entity.entity_id} at time {self.current_time}")

        logging.info(f"Event processing completed at time {self.current_time}")