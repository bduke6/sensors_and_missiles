class Event:
    def __init__(self, time, event_type, entity=None, target=None):
        self.time = time
        self.event_type = event_type
        self.entity = entity
        self.target = target
    
    def __lt__(self, other):
        return self.time < other.time

class LaunchEvent(Event):
    def __init__(self, time, entity, target):
        super().__init__(time, "Launch", entity, target)

class DetectEvent(Event):
    def __init__(self, time, entity, target):
        super().__init__(time, "Detect", entity, target)

class InterceptEvent(Event):
    def __init__(time, entity, target):
        super().__init__(time, "Intercept", entity, target)
