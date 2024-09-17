import numpy as np

def geodetic_to_ecef(lat, lon, alt):
    # WGS84 ellipsoid constants
    a = 6378137.0  # semi-major axis in meters
    f = 1 / 298.257223563  # flattening
    e2 = 2 * f - f ** 2  # square of eccentricity

    lat = np.radians(lat)
    lon = np.radians(lon)

    N = a / np.sqrt(1 - e2 * np.sin(lat) ** 2)
    X = (N + alt) * np.cos(lat) * np.cos(lon)
    Y = (N + alt) * np.cos(lat) * np.sin(lon)
    Z = (N * (1 - e2) + alt) * np.sin(lat)

    return X, Y, Z

def ecef_to_geodetic(X, Y, Z):
    # WGS84 ellipsoid constants
    a = 6378137.0  # semi-major axis in meters
    f = 1 / 298.257223563  # flattening
    e2 = 2 * f - f ** 2  # square of eccentricity
    b = a * (1 - f)

    lon = np.arctan2(Y, X)
    hyp = np.sqrt(X ** 2 + Y ** 2)
    lat = np.arctan2(Z, (1 - e2) * hyp)
    N = a / np.sqrt(1 - e2 * np.sin(lat) ** 2)
    alt = hyp / np.cos(lat) - N

    lat = np.degrees(lat)
    lon = np.degrees(lon)

    return lat, lon, alt

def calculate_distance_and_bearing(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance and initial bearing between two points
    on the Earth's surface specified in geodetic coordinates (lat/lon).
    """
    # Convert latitude and longitude from degrees to radians
    lat1 = np.radians(lat1)
    lon1 = np.radians(lon1)
    lat2 = np.radians(lat2)
    lon2 = np.radians(lon2)

    # Haversine formula for distance
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    distance = 6371000.0 * c  # Radius of Earth in meters

    # Formula for initial bearing
    y = np.sin(dlon) * np.cos(lat2)
    x = np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon)
    bearing = np.degrees(np.arctan2(y, x))

    # Normalize the bearing to 0-360 degrees
    bearing = (bearing + 360) % 360

    return distance, bearing