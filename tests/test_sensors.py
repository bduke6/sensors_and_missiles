import pytest
from src.sensors import Sensor

def test_sensor_detection():
    sensor = Sensor(location=[0, 0], range=1000)
    entity_position = [500, 0]
    assert sensor.detect(entity_position) == True

    entity_position = [1500, 0]
    assert sensor.detect(entity_position) == False
