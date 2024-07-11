import pytest
from src.events import Event, LaunchEvent, DetectEvent, InterceptEvent

def test_event_comparison():
    event1 = Event(time=1, event_type="Test")
    event2 = Event(time=2, event_type="Test")
    assert event1 < event2

def test_launch_event():
    launch_event = LaunchEvent(time=1, entity=None, target=None)
    assert launch_event.event_type == "Launch"
