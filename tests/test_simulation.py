import pytest
import numpy as np
from calculations import geodetic_to_ecef, ecef_to_geodetic
from environment import Environment  # Add this line
from entities import Entity, Missile, Ship, Aircraft
from events import Event  # Add this line

def test_geodetic_to_ecef():
    lat, lon, alt = 40.748817, -73.985428, 0
    X, Y, Z = geodetic_to_ecef(lat, lon, alt)
    assert np.isclose(X, 1334949.407, atol=1e-2)
    assert np.isclose(Y, -4651057.064, atol=1e-2)
    assert np.isclose(Z, 4141331.101, atol=1e-2)

def test_ecef_to_geodetic():
    X, Y, Z = 1334949.407, -4651057.064, 4141331.101
    lat, lon, alt = ecef_to_geodetic(X, Y, Z)
    assert np.isclose(lat, 40.748817, atol=1e-5)
    assert np.isclose(lon, -73.985428, atol=1e-5)
    assert np.isclose(alt, 0.0, atol=1e-4)

def test_entity_update_position():
    entity = Entity(lat=0, lon=0, alt=0, velocity=[1, 1, 1], orientation=[0, 0, 0], entity_id='test_entity')
    entity.update_position(1)
    assert entity.lat == 1
    assert entity.lon == 1
    assert entity.alt == 1

def test_missile_launch():
    missile = Missile(lat=0, lon=0, alt=0, velocity=[0, 0, 0], orientation=[0, 0, 0], entity_id='test_missile')
    target = Entity(lat=1, lon=1, alt=1, velocity=[0, 0, 0], orientation=[0, 0, 0], entity_id='target')
    missile.launch(target)
    assert missile.lat == 0
    assert missile.lon == 0
    assert missile.alt == 0

def test_ship_creation():
    ship = Ship(lat=0, lon=0, alt=0, velocity=[0, 0, 0], orientation=[0, 0, 0], entity_id='test_ship')
    assert ship.lat == 0
    assert ship.lon == 0
    assert ship.alt == 0

def test_aircraft_update():
    aircraft = Aircraft(lat=0, lon=0, alt=0, velocity=[1, 1, 1], orientation=[0, 0, 0], entity_id='test_aircraft')
    aircraft.update_position(1)
    assert aircraft.lat == 1
    assert aircraft.lon == 1
    assert aircraft.alt == 1

def test_environment_process_events():
    env = Environment()
    entity = Entity(lat=0, lon=0, alt=0, velocity=[1, 1, 1], orientation=[0, 0, 0], entity_id='test_entity')
    env.add_entity(entity)
    event = Event(time=1)
    env.schedule_event(event)
    env.process_events(10)
    assert env.current_time == 1
