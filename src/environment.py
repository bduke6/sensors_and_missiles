import heapq
import logging

class Environment:
    def __init__(self):
        self.event_queue = []  # Event priority queue
        self.current_time = 0  # Start time of the simulation
        self.entities = {}  # Dictionary to store entities by entity_id
        self.event_counter = 0  # Counter to uniquely identify events

    def time_to_seconds(self, time_str):
        """Convert HH:MM:SS time format to seconds."""
        hours, minutes, seconds = map(int, time_str.split(':'))
        return hours * 3600 + minutes * 60 + seconds

    def schedule_event(self, event):
        """Schedule an event in the environment."""
        if 'receiver' not in event:
            event['receiver'] = event['entity'].entity_id if 'entity' in event else None  # Ensure receiver is set
        
        event_time = self.time_to_seconds(event['time']) if isinstance(event['time'], str) else event['time']
        event_id = self.event_counter
        self.event_counter += 1

        # Push the event into the queue
        heapq.heappush(self.event_queue, (event_time, event_id, event))
        logging.info(f"Event scheduled at time {event_time} for {event['receiver']}")


    def add_entity(self, entity):
        """Add an entity to the environment."""
        self.entities[entity.entity_id] = entity
        logging.info(f"Entity {entity.entity_id} added to the environment.")

    def is_event_scheduled(self, event_type, entity_id, time):
        """Check if a specific event is scheduled for an entity."""
        for event_time, _, event in self.event_queue:
            if event_time == time and event.get('receiver') == entity_id and event['type'] == event_type:
                return True
        return False

    def clear_events(self, entity_id, event_type):
        """Clear all events of a specific type for an entity."""
        self.event_queue = [
            (time, idx, event) for time, idx, event in self.event_queue
            if not (event.get('receiver') == entity_id and event['type'] == event_type)
        ]
        heapq.heapify(self.event_queue)

    def process_events(self, max_time):
        """Process events from the queue up to the specified max time."""
        while self.event_queue and self.current_time <= max_time:
            event_time, _, event = heapq.heappop(self.event_queue)
            self.current_time = event_time

            # Find the target entity
            entity = self.entities.get(event.get('receiver'))
            if entity:
                # Process the event by passing relevant data to the entity
                entity.process_event({
                    'type': event['type'],
                    'time': event['time'],
                    'params': event['params']
                })
                logging.info(f"Processed event for {entity.entity_id} at time {self.current_time}")
            else:
                logging.warning(f"Entity {event.get('receiver')} not found for event processing.")

        logging.info(f"Event processing completed at time {self.current_time}")
