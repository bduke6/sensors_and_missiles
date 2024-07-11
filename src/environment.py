import heapq
from src.entities import Entity, Missile, Ship, Aircraft
from src.sensors import Sensor
from src.events import Event, LaunchEvent, DetectEvent, InterceptEvent

class Environment:
    def __init__(self):
        self.entities = []
        self.sensors = []
        self.event_queue = []
    
    def add_entity(self, entity):
        self.entities.append(entity)
    
    def add_sensor(self, sensor):
        self.sensors.append(sensor)
    
    def schedule_event(self, event):
        heapq.heappush(self.event_queue, event)
    
    def process_events(self, max_time):
        time = 0
        while self.event_queue and time < max_time:
            event = heapq.heappop(self.event_queue)
            time = event.time
            self.handle_event(event, time)
    
    def handle_event(self, event, time):
        if event.event_type == "Launch":
            print(f"Missile launched at time {time}")
            self.schedule_event(DetectEvent(time + 10, event.entity, event.target))  # Example detection time
        elif event.event_type == "Detect":
            print(f"Missile detected at time {time}")
            for sensor in self.sensors:
                if sensor.detect(event.entity.position[:2]):
                    print(f"Missile detected by sensor at {sensor.location}")
                    interceptor = Ship(sensor.location.coords[0], [50, 0, 0])  # Example interceptor
                    self.add_entity(interceptor)
                    interceptor.launch_missile(event.entity, self, time + 5)
        elif event.event_type == "Intercept":
            print(f"Missile intercepted at time {time}")
            # Handle interception logic
