from shapely.geometry import Point

class Sensor:
    def __init__(self, location, range):
        self.location = Point(location)
        self.range = range
        self.coverage_area = self.location.buffer(range)  # Circular coverage area
    
    def detect(self, entity_position):
        entity_point = Point(entity_position)
        return self.coverage_area.contains(entity_point)
