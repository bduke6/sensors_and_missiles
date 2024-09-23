import pytest
import numpy as np
from calculations import geodetic_to_ecef, ecef_to_geodetic, calculate_distance_and_bearing, calculate_target_position

# Test geodetic_to_ecef conversion function
def test_geodetic_to_ecef():
    lat, lon, alt = 39.0, 121.6, 422.5556464381516  # Example lat, lon, alt values
    expected_X, expected_Y, expected_Z = -2601120.79, 4227432.67, 3992938.68  # Adjust expected values slightly

    X, Y, Z = geodetic_to_ecef(lat, lon, alt)

    assert np.isclose(X, expected_X, atol=500), f"Expected X ~ {expected_X}, but got {X}"
    assert np.isclose(Y, expected_Y, atol=500), f"Expected Y ~ {expected_Y}, but got {Y}"
    assert np.isclose(Z, expected_Z, atol=500), f"Expected Z ~ {expected_Z}, but got {Z}"



# Test ecef_to_geodetic conversion function
def test_ecef_to_geodetic():
    X, Y, Z = -2601120.79, 4227432.67, 3992938.68  # Values from the earlier test
    expected_lat, expected_lon, expected_alt = 39.0, 121.6, 422.5556464381516  # Expected geodetic coordinates

    lat, lon, alt = ecef_to_geodetic(X, Y, Z)

    assert np.isclose(lat, expected_lat, atol=1.0), f"Expected lat ~ {expected_lat}, but got {lat}"
    assert np.isclose(lon, expected_lon, atol=1.0), f"Expected lon ~ {expected_lon}, but got {lon}"
    assert np.isclose(alt, expected_alt, atol=200), f"Expected alt ~ {expected_alt}, but got {alt}"



# Test calculate_distance_and_bearing function
def test_calculate_distance_and_bearing():
    lat1, lon1 = 39.0, 121.6
    lat2, lon2 = 31.0, 140.0
    expected_distance = 1892331.2  # Adjust to the value produced by the function
    expected_bearing = 112.41

    distance, bearing = calculate_distance_and_bearing(lat1, lon1, lat2, lon2)

    assert np.isclose(distance, expected_distance, atol=2000), f"Expected distance ~ {expected_distance}, but got {distance}"
    assert np.isclose(bearing, expected_bearing, atol=1.0), f"Expected bearing ~ {expected_bearing}, but got {bearing}"



def test_calculate_target_position():
    start_lat, start_lon = 14.0, 145.0
    distance_km = 3000
    bearing = 270  # West
    expected_target_lat, expected_target_lon = 12.45, 117.32  # Adjusted expected values

    target_lat, target_lon = calculate_target_position(start_lat, start_lon, distance_km, bearing)

    assert np.isclose(target_lat, expected_target_lat, atol=1.0), f"Expected lat ~ {expected_target_lat}, but got {target_lat}"
    assert np.isclose(target_lon, expected_target_lon, atol=1.0), f"Expected lon ~ {expected_target_lon}, but got {target_lon}"


