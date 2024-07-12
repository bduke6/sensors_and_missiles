# src/event_engine.py
import heapq

class Event:
    def __init__(self, time, action):
        self.time = time
        self.action = action

    def __lt__(self, other):
        return self.time < other.time

class EventEngine:
    def __init__(self):
        self.events = []
        self.current_time = 0

    def schedule_event(self, event):
        heapq.heappush(self.events, event)

    def run(self, max_time):
        while self.events and self.current_time <= max_time:
            event = heapq.heappop(self.events)
            self.current_time = event.time
            event.action(self)
