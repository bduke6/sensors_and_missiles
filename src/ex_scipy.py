import numpy as np
from scipy.integrate import solve_ivp
import pymap3d as pm
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# Constants
g = 9.81  # Earth's gravity in m/s^2
rho = 1.225  # Air density at sea level (kg/m^3)
C_d = 0.01  # Drag coefficient (reduced for high-velocity missile)
A = 0.1  # Cross-sectional area of the missile (m^2)
mass = 1000  # Mass of the missile in kg

# Define the system of differential equations for position and velocity
def missile_dynamics(t, state):
    # Unpack the state vector
    x, y, z, vx, vy, vz = state
    
    # Compute the speed (magnitude of the velocity)
    speed = np.sqrt(vx**2 + vy**2 + vz**2)
    
    # Gravity force (constant downward force in Z-direction)
    F_gravity = np.array([0, 0, -mass * g])
    
    # Drag force (proportional to the square of the velocity)
    F_drag = -0.5 * rho * C_d * A * speed * np.array([vx, vy, vz])
    
    # Net force (gravity + drag)
    F_net = F_gravity + F_drag
    
    # Acceleration = Net Force / Mass
    ax, ay, az = F_net / mass
    
    # Print monitoring variables for forces, speed, and position
    heading_instant = np.degrees(np.arctan2(vy, vx))  # Calculate instantaneous heading
    print(f"Time: {t:.2f} s | Speed: {speed:.2f} m/s | Heading: {heading_instant:.2f}° | Drag: {F_drag} | Gravity: {F_gravity}")
    
    # Return derivatives: [dx/dt, dy/dt, dz/dt, dvx/dt, dvy/dt, dvz/dt]
    return [vx, vy, vz, ax, ay, az]

# Initial conditions: position (x, y, z) and velocity (vx, vy, vz)
lat_launch, lon_launch, alt_launch = 37.7749, -122.4194, 1000  # San Francisco
x_ecef, y_ecef, z_ecef = pm.geodetic2ecef(lat_launch, lon_launch, alt_launch)

# Simplified initial velocity
velocity_initial = 5000  # m/s

# Instead of ENU to ECEF, directly initialize the velocity in ECEF
vx_ecef = velocity_initial  # Assume eastward for simplicity
vy_ecef = 0  # No initial velocity in Y-direction
vz_ecef = 0  # No initial velocity in Z-direction

# Initial state vector: [x, y, z, vx, vy, vz]
initial_state = [x_ecef, y_ecef, z_ecef, vx_ecef, vy_ecef, vz_ecef]


# Initial state vector: [x, y, z, vx, vy, vz]
initial_state = [x_ecef, y_ecef, z_ecef, vx_ecef, vy_ecef, vz_ecef]

# Time span for the simulation
t_span = (0, 60)  # 60 seconds

# Solve the differential equations using `solve_ivp` with a finer time step (6000 points)
sol = solve_ivp(missile_dynamics, t_span, initial_state, t_eval=np.linspace(0, 60, 6000))

# Extract the solution
x_sol = sol.y[0]
y_sol = sol.y[1]
z_sol = sol.y[2]

# Convert the trajectory from ECEF to geodetic coordinates for plotting
trajectory_geodetic = [pm.ecef2geodetic(x_sol[i], y_sol[i], z_sol[i]) for i in range(len(x_sol))]

# Convert trajectory data to a numpy array for easier plotting
trajectory_geodetic = np.array(trajectory_geodetic)

# Extract latitudes and longitudes for plotting
lats = trajectory_geodetic[:, 0]
lons = trajectory_geodetic[:, 1]

# Plot the missile's flight path on a map using Basemap
plt.figure(figsize=(10, 8))
m = Basemap(projection='merc', llcrnrlat=36, urcrnrlat=38, llcrnrlon=-123, urcrnrlon=-121, resolution='i')
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
