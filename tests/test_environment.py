import sys
sys.path.append('src')


# tests/test_environment.py

import pytest
from environment import Environment
from entities import Missile, Ship, Aircraft
from sensors import Sensor
from events import LaunchEvent

def test_environment_add_entity():
    env = Environment()
    missile = Missile(lat=0, lon=0, alt=0, velocity=[1, 1, 1], orientation=[1, 0, 0], entity_id="missile_1")
    env.add_entity(missile)
    assert missile in env.entities

def test_environment_add_sensor():
    env = Environment()
    sensor = Sensor(location=[0, 0], alt=0, range=1000)
    env.add_sensor(sensor)
    assert sensor in env.sensors

def test_environment_schedule_event():
    env = Environment()
    event = LaunchEvent(time=1, entity=None, target=None)
    env.schedule_event(event)
    assert env.event_queue[0] == event

def test_environment_process_events():
    env = Environment()
    missile = Missile(lat=0, lon=0, alt=0, velocity=[1, 1, 1], orientation=[1, 0, 0], entity_id="missile_1")
    ship = Ship(lat=0, lon=0, alt=0, velocity=[0, 0, 0], orientation=[1, 0, 0], entity_id="ship_1")
    env.add_entity(missile)
    env.add_entity(ship)
    event = LaunchEvent(time=0, entity=missile, target=ship)
    env.schedule_event(event)
    env.process_events(max_time=10)
    assert missile.lat != 0  # Ensure the missile has moved