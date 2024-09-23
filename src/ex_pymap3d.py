import pymap3d as pm
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# Constants
g = 9.81  # Earth's gravity in m/s^2
R = 6371000  # Approximate radius of the Earth in meters

# Missile launch parameters
lat_launch = 37.7749  # Latitude of the launch site (San Francisco)
lon_launch = -122.4194  # Longitude of the launch site (San Francisco)
alt_launch = 1000  # Altitude in meters (1 km above ground)

velocity_initial = 300000 # Initial velocity in m/s
pitch = 45  # Pitch angle in degrees
heading = 270  # Heading (azimuth) angle in degrees, 0 = north, 90 = east

# Convert pitch and heading to radians
pitch_rad = np.radians(pitch)
heading_rad = np.radians(heading)

# Simulation time parameters
time_step = 0.1  # Time step in seconds
total_time = 60  # Maximum simulation time in seconds

# Missile initial position in ECEF
x_ecef, y_ecef, z_ecef = pm.geodetic2ecef(lat_launch, lon_launch, alt_launch)

# Convert the geodetic launch site to an ENU origin (the same point)
enu_origin = pm.geodetic2ecef(lat_launch, lon_launch, alt_launch)

# Calculate initial velocity components in ENU frame
v_east = velocity_initial * np.cos(pitch_rad) * np.sin(heading_rad)  # Eastward velocity
v_north = velocity_initial * np.cos(pitch_rad) * np.cos(heading_rad)  # Northward velocity
v_up = velocity_initial * np.sin(pitch_rad)  # Upward velocity

# Combine ENU velocity vector
velocity_enu = np.array([v_east, v_north, v_up])

# Transform velocity from ENU to ECEF
vx_ecef, vy_ecef, vz_ecef = pm.enu2ecef(v_east, v_north, v_up, lat_launch, lon_launch, alt_launch)

# Store the initial ECEF velocity vector
velocity_ecef = np.array([vx_ecef, vy_ecef, vz_ecef])

# Initialize arrays to store the trajectory for plotting and analysis
trajectory_geodetic = [[lat_launch, lon_launch, alt_launch]]

# Initialize position vector in ECEF
position_ecef = np.array([x_ecef, y_ecef, z_ecef])

# Simulation loop to calculate the trajectory
for t in np.arange(0, total_time, time_step):
    # Update velocity (considering gravity, only affects the vertical component in ECEF)
    velocity_ecef[2] -= g * time_step  # Gravity affects the Z (up/down) component in ECEF

    # Update position in ECEF based on the velocity
    position_ecef += velocity_ecef * time_step

    # Convert the new ECEF position to geodetic coordinates for plotting
    lat, lon, alt = pm.ecef2geodetic(position_ecef[0], position_ecef[1], position_ecef[2])
    
    # Store the new geodetic coordinates
    trajectory_geodetic.append([lat, lon, alt])

    # Stop the simulation if the missile hits the ground (alt <= 0)
    if alt <= 0:
        break

# Convert trajectory data to a numpy array for easier plotting
trajectory_geodetic = np.array(trajectory_geodetic)

# Extract latitudes and longitudes for plotting
lats = trajectory_geodetic[:, 0]
lons = trajectory_geodetic[:, 1]

# Plot the missile's flight path on a map using Basemap
plt.figure(figsize=(10, 8))
m = Basemap(projection='merc', llcrnrlat=36, urcrnrlat=38, llcrnrlon=-123, urcrnrlon=-122, resolution='i')
m.drawcoastlines()
m.drawcountries()
m.drawstates()
m.drawmapboundary(fill_color='aqua')
m.fillcontinents(color='lightgray', lake_color='aqua')
m.drawparallels(np.arange(-90., 91., 2.), labels=[1, 0, 0, 0])
m.drawmeridians(np.arange(-180., 181., 2.), labels=[0, 0, 0, 1])

# Convert lat/lon to the map projection coordinates and plot
x, y = m(lons, lats)
m.plot(x, y, marker='o', color='r', markersize=5, linewidth=2)

plt.title("Missile Flight Path on Map")
plt.show()
