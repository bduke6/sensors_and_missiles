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
