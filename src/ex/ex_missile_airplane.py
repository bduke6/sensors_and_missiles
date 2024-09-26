import numpy as np
from pymap3d import geodetic2ecef
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import time

# Constants for the airplanes
v_initial_plane1 = 200  # speed in m/s for the first airplane
v_initial_plane2 = 150  # speed in m/s for the second airplane
lat_plane1 = 32.3  # latitude of first airplane launch point
lon_plane1 = -106.5  # longitude of first airplane launch point
altitude_plane1 = 3000  # altitude of first airplane in meters
lat_plane2 = 32.35  # latitude of second airplane launch point
lon_plane2 = -106.55  # longitude of second airplane launch point
altitude_plane2 = 3100  # altitude of second airplane in meters

# Time step and total simulation time
dt = 1.0  # seconds
simulation_time = 60  # run the simulation for 60 seconds

# Set up Basemap for visualization
m = Basemap(projection='merc', llcrnrlat=32, urcrnrlat=33, llcrnrlon=-107, urcrnrlon=-106, resolution='l')
m.drawcoastlines()
m.drawcountries()
m.drawparallels(np.arange(-90, 91, 0.1), labels=[1, 0, 0, 0])
m.drawmeridians(np.arange(-180, 181, 0.1), labels=[0, 0, 0, 1])

# Function to update the position of an airplane
def update_position(lat, lon, alt, heading, speed, dt):
    # Calculate change in lat, lon assuming the earth is flat for simplicity
    distance = speed * dt
    lat_new = lat + (distance / 111320) * np.cos(np.radians(heading))  # 1 degree lat = 111320 meters
    lon_new = lon + (distance / (111320 * np.cos(np.radians(lat)))) * np.sin(np.radians(heading))
    return lat_new, lon_new, alt

# Function to calculate the relative position between two airplanes
def calculate_relative_position(lat1, lon1, alt1, heading1, lat2, lon2, alt2):
    # Convert lat, lon, altitude to ECEF for both airplanes
    x1, y1, z1 = geodetic2ecef(lat1, lon1, alt1)
    x2, y2, z2 = geodetic2ecef(lat2, lon2, alt2)

    # Calculate relative distance in ECEF
    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1

    # Calculate horizontal distance
    horizontal_distance = np.sqrt(dx ** 2 + dy ** 2)

    # Calculate relative bearing (clock position)
    bearing = np.degrees(np.arctan2(dy, dx))
    relative_bearing = (bearing - heading1) % 360

    # Calculate relative elevation
    vertical_distance = dz
    slant_angle = np.degrees(np.arctan2(vertical_distance, horizontal_distance))

    # Convert relative bearing to clock position
    clock_position = round((relative_bearing / 30) % 12) or 12

    # Return relative distance, clock position, and slant angle
    return horizontal_distance, clock_position, slant_angle

# Initial airplane positions and headings
lat_current_plane1, lon_current_plane1, alt_current_plane1 = lat_plane1, lon_plane1, altitude_plane1
lat_current_plane2, lon_current_plane2, alt_current_plane2 = lat_plane2, lon_plane2, altitude_plane2
heading_plane1 = 300  # heading of the first airplane
heading_plane2 = 120  # heading of the second airplane, crossing at an angle

# Simulation loop
for t in range(simulation_time):
    # Update positions of both airplanes
    lat_current_plane1, lon_current_plane1, alt_current_plane1 = update_position(
        lat_current_plane1, lon_current_plane1, alt_current_plane1, heading_plane1, v_initial_plane1, dt)
    
    lat_current_plane2, lon_current_plane2, alt_current_plane2 = update_position(
        lat_current_plane2, lon_current_plane2, alt_current_plane2, heading_plane2, v_initial_plane2, dt)
    
    # Calculate relative position from airplane 1 to airplane 2
    distance, clock_position, slant_angle = calculate_relative_position(
        lat_current_plane1, lon_current_plane1, alt_current_plane1, heading_plane1,
        lat_current_plane2, lon_current_plane2, alt_current_plane2)

    # Output the relative position in pilot language
    print(f"Time {t} seconds: Airplane 2 is at {clock_position} o'clock, "
          f"{distance:.2f} meters away, with a slant angle of {slant_angle:.2f}°")

    # Plot airplane positions on the map
    x1, y1 = m(lon_current_plane1, lat_current_plane1)
    x2, y2 = m(lon_current_plane2, lat_current_plane2)
    m.plot(x1, y1, 'bo', markersize=5)  # Airplane 1 in blue
    m.plot(x2, y2, 'ro', markersize=5)  # Airplane 2 in red

    # Pause for visualization
    plt.pause(0.1)

# Show the final map
plt.show()