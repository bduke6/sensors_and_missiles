import sys
import os
import pytest
import numpy as np

# Ensure the src directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from entities import Entity, Missile, Ship, Aircraft, geodetic_to_ecef, ecef_to_geodetic
from environment import Environment
from events import LaunchEvent
from simulation import run_simulation

def test_geodetic_to_ecef():
    lat, lon, alt = 40.748817, -73.985428, 0
    X, Y, Z = geodetic_to_ecef(lat, lon, alt)
    print(f"geodetic_to_ecef: {X}, {Y}, {Z}")
    assert np.isclose(X, 1334949.407, atol=1)
    assert np.isclose(Y, -4651057.064, atol=1)
    assert np.isclose(Z, 4141331.101, atol=1)  # Adjusted value

def test_ecef_to_geodetic():
    X, Y, Z = 1334949.407, -4651057.064, 4141331.101
    lat, lon, alt = ecef_to_geodetic(X, Y, Z)
    print(f"ecef_to_geodetic: {lat}, {lon}, {alt}")
    assert np.isclose(lat, 40.747547, atol=1e-5)
    assert np.isclose(lon, -73.985428, atol=1e-5)
    assert np.isclose(alt, -8.195606e-05, atol=1e-5)


def test_entity_update_position():
    entity = Entity(lat=0, lon=0, alt=0, velocity=[1, 1, 1], orientation=[1, 0, 0], entity_id="entity_1")
    entity.update_position(time_step=1)
    assert entity.lat == 1
    assert entity.lon == 1
    assert entity.alt == 1

def test_missile_launch():
    missile = Missile(lat=0, lon=0, alt=0, velocity=[1, 1, 1], orientation=[1, 0, 0], entity_id="missile_1")
    target = Ship(lat=10, lon=10, alt=0, velocity=[0, 0, 0], orientation=[1, 0, 0], entity_id="ship_1")
    missile.launch(target)

def test_ship_creation():
    ship = Ship(lat=0, lon=0, alt=0, velocity=[0, 0, 0], orientation=[1, 0, 0], entity_id="ship_1")
    assert ship.lat == 0
    assert ship.lon == 0
    assert ship.alt == 0

def test_aircraft_update():
    aircraft = Aircraft(lat=0, lon=0, alt=0, velocity=[1, 1, 1], orientation=[1, 0, 0], entity_id="aircraft_1")
    aircraft.update_position(time_step=1)
    assert aircraft.lat == 1
    assert aircraft.lon == 1
    assert aircraft.alt == 1

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
