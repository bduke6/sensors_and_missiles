import pytest
from src.environment import Environment
from src.entities import Missile, Ship, Aircraft
from src.sensors import Sensor
from src.events import LaunchEvent, DetectEvent, InterceptEvent

def test_environment_add_entity():
    env = Environment()
    missile = Missile(position=[0, 0, 0], velocity=[1, 1, 1])
    env.add_entity(missile)
    assert missile in env.entities

def test_environment_add_sensor():
    env = Environment()
    sensor = Sensor(location=[0, 0], range=1000)
    env.add_sensor(sensor)
    assert sensor in env.sensors

def test_environment_schedule_event():
    env = Environment()
    event = LaunchEvent(time=1, entity=None, target=None)
    env.schedule_event(event)
    assert env.event_queue[0] == event

def test_environment_process_events():
    env = Environment()
    missile = Missile(position=[0, 0, 0], velocity=[1, 1, 1])
    env.add_entity(missile)
    event = LaunchEvent(time=1, entity=missile, target=None)
    env.schedule_event(event)
    env.process_events(max_time=2)
    assert missile in env.entities  # Ensure missile is still in entities after processing
