import numpy as np

class Entity:
    def __init__(self, lat, lon, alt, velocity, orientation, entity_id):
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.velocity = np.array(velocity)
        self.orientation = np.array(orientation)
        self.entity_id = entity_id

    def update_position(self, time_step):
        self.lat += self.velocity[0] * time_step
        self.lon += self.velocity[1] * time_step
        self.alt += self.velocity[2] * time_step
    
    def update(self, time_step):
        self.update_position(time_step)

class Missile(Entity):
    def __init__(self, lat, lon, alt, velocity, orientation, entity_id):
        super().__init__(lat, lon, alt, velocity, orientation, entity_id)

    def launch(self, target):
        print(f"Launching missile {self.entity_id} towards target at {target.lat}, {target.lon}, {target.alt}")

class Ship(Entity):
    def __init__(self, lat, lon, alt, velocity, orientation, entity_id):
        super().__init__(lat, lon, alt, velocity, orientation, entity_id)

class Aircraft(Entity):
    def __init__(self, lat, lon, alt, velocity, orientation, entity_id):
        super().__init__(lat, lon, alt, velocity, orientation, entity_id)


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
    r = np.sqrt(X**2 + Y**2)
    E2 = a**2 - b**2
    F = 54 * b**2 * Z**2
    G = r**2 + (1 - e2) * Z**2 - e2 * E2
    c = (e2**2 * F * r**2) / (G**3)
    s = (1 + c + np.sqrt(c**2 + 2*c))**(1/3)
    P = F / (3 * (s + 1/s + 1)**2 * G**2)
    Q = np.sqrt(1 + 2 * e2**2 * P)
    r0 = -(P * e2 * r) / (1 + Q) + np.sqrt(0.5 * a**2 * (1 + 1/Q) - P * (1 - e2) * Z**2 / (Q * (1 + Q)) - 0.5 * P * r**2)
    U = np.sqrt((r - e2 * r0)**2 + Z**2)
    V = np.sqrt((r - e2 * r0)**2 + (1 - e2) * Z**2)
    Z0 = b**2 * Z / (a * V)

    alt = U * (1 - b**2 / (a * V))
    lat = np.arctan((Z + e2 * Z0) / r)
    lon = np.degrees(lon)
    lat = np.degrees(lat)

    return lat, lon, alt
