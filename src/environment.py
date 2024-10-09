import heapq
import logging

class Environment:
    def __init__(self):
        self.event_queue = []  # Event priority queue
        self.current_time = 0  # Start time of the simulation
        self.entities = {}  # Dictionary to store entities by entity_id
        self.event_counter = 0  # Counter to ensure unique event ordering

    @staticmethod
    def time_to_seconds(time_str):
        """Convert HH:MM:SS time format to seconds."""
        hours, minutes, seconds = map(int, time_str.split(':'))
        return hours * 3600 + minutes * 60 + seconds

    def add_entity(self, entity):
        """Add an entity to the environment."""
        self.entities[entity.entity_id] = entity
        logging.info(f"Entity {entity.entity_id} added to the environment.")

    def schedule_event(self, event):
        """Schedule an event in the environment from a C2 dictionary."""
        event_time = self.time_to_seconds(event['time'])  # Convert time to seconds
        # Increment the counter to ensure uniqueness in the heap
        self.event_counter += 1
        heapq.heappush(self.event_queue, (event_time, self.event_counter, event))
        logging.info(f"Event scheduled at time {event_time} for {event['receiver']}")

    def is_event_scheduled(self, event_type, entity_id, time):
        """Check if an event of a specific type is scheduled for an entity at a given time."""
        for event_time, _, event in self.event_queue:
            if event_time == time and event['receiver'] == entity_id and event['message_type'] == event_type:
                return True
        return False

    def clear_events(self, entity_id, event_type):
        """Remove all events of a specific type for a given entity from the event queue."""
        self.event_queue = [(time, idx, event) for time, idx, event in self.event_queue 
                            if not (event['receiver'] == entity_id and event['message_type'] == event_type)]
        
        heapq.heapify(self.event_queue)
        logging.info(f"Cleared all '{event_type}' events for entity {entity_id}.")

    def process_events(self, max_time):
        """Process all events until max_time is reached or no events are left."""
        while self.event_queue and self.current_time < max_time:
            event_time, _, event = heapq.heappop(self.event_queue)
            self.current_time = event_time

            logging.info(f"Event queue size: {len(self.event_queue)}")

            entity = self.entities.get(event['receiver'])
            if entity:
                entity.process_event({
                    'type': event['message_type'],
                    'time': event['time'],
                    'params': event['parameters']
                })
                logging.info(f"Processed event for {entity.entity_id} at time {self.current_time}")
            else:
                logging.warning(f"Entity {event['receiver']} not found for event processing.")

        logging.info(f"Event processing completed at time {self.current_time}")