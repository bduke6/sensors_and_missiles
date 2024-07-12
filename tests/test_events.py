import sys
sys.path.append('src')

import pytest
from events import Event, LaunchEvent, DetectEvent, InterceptEvent

class Event:
    def __init__(self, time, entity):
        self.time = time
        self.entity = entity

    def process(self, environment):
        raise NotImplementedError("Subclasses should implement this!")

    def __lt__(self, other):
        return self.time < other.time

    def __eq__(self, other):
        return self.time == other.time and self.entity == other.entity


def test_event_comparison():
    event1 = Event(time=1, entity="TestEntity1")
    event2 = Event(time=2, entity="TestEntity2")
    assert event1 < event2

def test_launch_event():
    launch_event = LaunchEvent(time=1, entity=None, target=None)
    assert launch_event.time == 1
