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
