import numpy as np

class Sensor:
    def __init__(self, location, range, alt=0):
        self.location = location
        self.range = range
        self.alt = alt
        self.detected_entities = []

    def detect(self, entity_position):
        # Ensure entity position includes altitude
        if len(entity_position) == 2:
            entity_position = np.append(entity_position, [0])
        distance = np.linalg.norm(np.array(self.location + [self.alt]) - np.array(entity_position))
        return distance <= self.range
