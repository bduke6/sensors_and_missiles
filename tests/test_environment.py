import pytest
from src.environment import Environment
from src.entities import Missile
from src.events import LaunchEvent

def test_environment_add_entity():
    env = Environment()
    missile = Missile(position=[0, 0, 0], velocity=[1, 1, 1])
    env.add_entity(missile)
    assert missile in env.entities

def test_environment_schedule_event():
    env = Environment()
    event = LaunchEvent(time=1, entity=None, target=None)
    env.schedule_event(event)
    assert env.event_queue[0] == event
