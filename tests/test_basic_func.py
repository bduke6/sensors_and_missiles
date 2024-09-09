import pytest
from entities import Entity

def test_entity_initialization():
    entity = Entity(lat=10.0, lon=20.0, alt=100, velocity=[0, 0, 0], orientation=[0, 0, 0], entity_id='test_entity')
    assert entity.lat == 10.0
    assert entity.lon == 20.0
    assert entity.alt == 100
    assert entity.velocity == [0, 0, 0]
    assert entity.orientation == [0, 0, 0]
    assert entity.entity_id == 'test_entity'


from unittest.mock import Mock
from entities import Missile, Entity
from events import LaunchEvent, MovementEvent

def test_missile_launch():
    missile = Missile(lat=10, lon=20, alt=0, velocity=[0, 0, 0], orientation=[0, 0, 0], entity_id='missile_1', fuel=100)
    target = Entity(lat=30, lon=40, alt=0, velocity=[0, 0, 0], orientation=[0, 0, 0], entity_id='target_1')
    environment = Mock()
    
    missile.launch(target, environment)
    assert missile.fuel == 100  # Example assertion, can adjust based on desired behavior


def test_launch_event():
    missile = Missile(lat=10, lon=20, alt=0, velocity=[0, 0, 0], orientation=[0, 0, 0], entity_id='missile_1', fuel=100)
    target = Entity(lat=30, lon=40, alt=0, velocity=[0, 0, 0], orientation=[0, 0, 0], entity_id='target_1')
    environment = Mock()
    
    event = LaunchEvent(time=1, missile=missile, target=target)
    event.process(environment)  # Should log the event

def test_missile_movement():
    missile = Missile(lat=10, lon=20, alt=0, velocity=[1, 1, 1], orientation=[0, 0, 0], entity_id='missile_1', fuel=100)
    environment = Mock()

    movement_event = MovementEvent(time=1, entity=missile)
    movement_event.process(environment)

    assert missile.lat == 10.1
    assert missile.lon == 20.1
    assert missile.alt == 0.1

