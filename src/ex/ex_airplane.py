import numpy as np
from pymap3d import aer2enu, enu2ecef, ecef2geodetic
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

# Constants
v_initial = 5000  # initial speed in m/s
lat_launch = 32.3  # latitude of launch point
lon_launch = -106.5  # longitude of launch point
altitude = 304.8  # 1000 ft in meters
acceleration = 1  # constant acceleration in m/s²
v_current = v_initial  # initialize current speed

# Time step
dt = 1.0  # seconds

# Initial heading
heading_initial = 330  # in degrees

# Set up Basemap for visualization
m = Basemap(projection='merc', llcrnrlat=31, urcrnrlat=38, llcrnrlon=-109, urcrnrlon=-104, resolution='l')
m.drawcoastlines()
m.drawcountries()
m.drawparallels(np.arange(-90, 91, 30), labels=[1, 0, 0, 0])
m.drawmeridians(np.arange(-180, 181, 60), labels=[0, 0, 0, 1])

# Function to update position in ECEF and convert back to lat/lon
def update_position(lat, lon, alt, heading, speed, dt):
    # Convert AER (heading) to ENU (east, north, up)
    v_east, v_north, v_up = aer2enu(heading, 0, speed)

    # Convert ENU to ECEF
    x_ecef, y_ecef, z_ecef = enu2ecef(v_east * dt, v_north * dt, v_up * dt, lat, lon, alt)

    # Update ECEF position
    lat_new, lon_new, alt_new = ecef2geodetic(x_ecef, y_ecef, z_ecef)

    return lat_new, lon_new, alt_new

# Initial position
lat_current, lon_current, alt_current = lat_launch, lon_launch, altitude

# Set up color mapping for speed visualization
cmap = plt.cm.get_cmap('coolwarm')  # color map from blue (low) to red (high)
v_min = v_initial  # minimum speed for color mapping
v_max = v_initial + acceleration * 25  # max speed during acceleration

# Initialize plot
plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots()

# Simulation loop
for t in range(100):
    if t == 30:
        heading_initial = 360  # change heading at 30 seconds
    elif t == 45:
        heading_initial = 130  # change heading again at 45 seconds

    # Apply acceleration between time 25 and 50
    if 25 <= t <= 50:
        v_current += acceleration * dt  # increase speed with constant acceleration
    elif t > 50:
        v_current = v_initial  # reset to initial speed after time 50

    # Update position
    lat_current, lon_current, alt_current = update_position(lat_current, lon_current, alt_current, heading_initial, v_current, dt)

    # Convert to map projection
    x, y = m(lon_current, lat_current)

    # Map speed to color (blue for slow, red for fast)
    color = cmap((v_current - v_min) / (v_max - v_min))  # Normalize speed for color map

    # Plot position on map with color based on speed
    m.plot(x, y, marker='o', markersize=5, color=color)

    # Update plot dynamically
    plt.draw()
    plt.pause(0.1)  # Pause to update the figure

    # Display info
    print(f"Time: {t:5.2f} s | Position: [{lat_current:.6f}, {lon_current:.6f}, {alt_current:.2f}] | Speed: {v_current:.2f} m/s | Heading: {heading_initial:.2f}°")

# Turn off interactive mode
plt.ioff()
plt.show()
