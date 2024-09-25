class SimulationEvent:
    def __init__(self, time, entity, event_type, params):
        self.time = time  # Event time
        self.entity = entity  # The entity associated with the event
        self.event_type = event_type  # Type of the event, e.g., 'move'
        self.params = params  # Event parameters, e.g., target_lat, target_lon, speed

    def __lt__(self, other):
        """This ensures that events are sorted by their time."""
        return self.time < other.time

    def __repr__(self):
        return f"<SimulationEvent time={self.time}, entity={self.entity.entity_id}, type={self.event_type}>"