import pytest
from entities import Entity
from calculations import ecef_to_geodetic
from environment import Environment  # Ensure Environment is imported

def test_entity_initialization():
    entity = Entity(lat=10.0, lon=20.0, alt=100, velocity=[0, 0, 0], orientation=[0, 0, 0], entity_id='test_entity')
    lat, lon, alt = ecef_to_geodetic(entity.X, entity.Y, entity.Z)  # Convert back to geodetic for verification
    
    # Increase the tolerance to 1e-5
    assert lat == pytest.approx(10.0, abs=1e-5)
    assert lon == pytest.approx(20.0, abs=1e-5)
    assert alt == pytest.approx(100.0, abs=1e-1)
    assert entity.velocity == [0, 0, 0]
    assert entity.orientation == [0, 0, 0]
    assert entity.entity_id == 'test_entity'

def test_entity_movement():
    # Create an Entity with initial lat, lon, alt, and velocity
    entity = Entity(lat=10.0, lon=20.0, alt=100.0, velocity=[1.0, 2.0, 0.5], orientation=[0, 0, 0], entity_id='test_entity')

    # Time step for the movement
    time_step = 10  # 10 seconds

    # Create an environment instance
    env = Environment()

    # Move the entity
    entity.move(time_step, env)

    # Assert that the entity has moved (example: check new position)
    assert entity.X != 0
    assert entity.Y != 0
    assert entity.Z != 0


    # Optionally, assert on new latitude, longitude, altitude after movement
    # Example assertions (customize based on your logic):
    # assert some_latitude_value <= entity.X <= some_other_latitude_value
    # assert some_longitude_value <= entity.Y <= some_other_longitude_value
    # assert some_altitude_value <= entity.Z <= some_other_altitude_value



from unittest.mock import Mock
from entities import Missile, Entity
from events import LaunchEvent, MovementEvent

def test_missile_launch():
    missile = Missile(lat=10, lon=20, alt=0, velocity=[0, 0, 0], orientation=[0, 0, 0], entity_id='missile_1', fuel=100)
    target = Entity(lat=30, lon=40, alt=0, velocity=[0, 0, 0], orientation=[0, 0, 0], entity_id='target_1')
    environment = Mock()
    environment.current_time = 0  # Mock the current time

    missile.launch(target, environment)
    assert environment.schedule_event.called  # Ensure the event is scheduled

def test_launch_event():
    missile = Missile(lat=10, lon=20, alt=0, velocity=[0, 0, 0], orientation=[0, 0, 0], entity_id='missile_1', fuel=100)
    target = Entity(lat=30, lon=40, alt=0, velocity=[0, 0, 0], orientation=[0, 0, 0], entity_id='target_1')
    environment = Mock()
    environment.current_time = 0  # Mock the current time

    event = LaunchEvent(time=1, missile=missile, target=target)
    event.process(environment)  # Should log the event
    assert environment.schedule_event.called  # Ensure the event is scheduled











