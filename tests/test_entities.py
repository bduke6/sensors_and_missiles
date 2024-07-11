import pytest
import numpy as np
from src.entities import Entity, Missile, Ship, Aircraft

def test_entity_update_position():
    entity = Entity(position=[0, 0, 0], velocity=[1, 1, 1])
    entity.update_position(1)
    assert np.array_equal(entity.position, [1, 1, 1])

def test_missile_creation():
    missile = Missile(position=[0, 0, 0], velocity=[1, 1, 1])
    assert np.array_equal(missile.position, [0, 0, 0])
    assert np.array_equal(missile.velocity, [1, 1, 1])

def test_ship_creation():
    ship = Ship(position=[-500, 0, 0], velocity=[10, 0, 0])
    assert np.array_equal(ship.position, [-500, 0, 0])
    assert np.array_equal(ship.velocity, [10, 0, 0])

def test_aircraft_creation():
    aircraft = Aircraft(position=[0, 1000, 0], velocity=[200, 0, 0])
    assert np.array_equal(aircraft.position, [0, 1000, 0])
    assert np.array_equal(aircraft.velocity, [200, 0, 0])
