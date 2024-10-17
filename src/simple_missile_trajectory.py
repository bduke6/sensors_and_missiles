import pymap3d as pm
import matplotlib.pyplot as plt

# Launch and target parameters
start_lat, start_lon, start_alt = 5.0, 110.0, 0  # Start point
target_lat, target_lon, target_alt = 25.0, 120.5, 0  # Ground level target

# Missile parameters
vertical_velocity = 5000  # Initial upward velocity (m/s)
horizontal_velocity = 2500  # Horizontal velocity (m/s) for longer range
g = 9.81  # Gravity in m/s^2
time_step = 1  # Time step in seconds
max_steps = 5000  # Upper bound for steps; we'll terminate early upon impact

# Lists to store trajectory data
altitudes = []
ground_distances = []

# Initialize ENU coordinates
up = 0  # Altitude in ENU frame, initially 0
east = 0
north = 0

# Store initial ECEF coordinates for reference
x0, y0, z0 = pm.geodetic2ecef(start_lat, start_lon, start_alt)

apogee_reached = False
impact_time = None
impact_distance = None

# Simulate the ballistic trajectory
for step in range(max_steps):
    if not apogee_reached:
        # Boost phase - missile gains altitude
        up += vertical_velocity * time_step
        vertical_velocity -= g * time_step  # Reduce vertical velocity due to gravity
        
        # Transition to descent phase when vertical velocity reaches zero (apogee)
        if vertical_velocity <= 0:
            apogee_reached = True
            vertical_velocity = 0  # Stop upward movement initially after apogee
    else:
        # Descent phase - gravity pulls the missile down
        vertical_velocity -= g * time_step  # Gravity accelerates the descent
        up += vertical_velocity * time_step  # Continue descent

    # Horizontal movement toward target in ENU frame
    east += horizontal_velocity * time_step

    # Convert ENU to ECEF for plotting
    x, y, z = pm.enu2ecef(east, north, up, start_lat, start_lon, start_alt)

    # Convert ECEF to geodetic for altitude and distance
    lat, lon, alt = pm.ecef2geodetic(x, y, z)
    altitudes.append(alt)

    # Calculate horizontal ground distance in km
    ground_distance = east / 1000  # Convert to km (as east represents horizontal distance here)
    ground_distances.append(ground_distance)

    # Check for impact (altitude at or below target altitude)
    if alt <= target_alt:
        impact_time = step * time_step  # Calculate the impact time in seconds
        impact_distance = ground_distance  # Distance in km at impact
        break  # Exit the loop once impact is detected

    # Print step details (optional)
    print(f"Time Step {step + 1}: Altitude = {alt:.2f} m, Ground Distance = {ground_distance:.2f} km")

# Plotting the ballistic trajectory
plt.figure()
plt.plot(ground_distances, altitudes, color="blue", label="Ballistic Path")
plt.axvline(x=impact_distance, color="red", linestyle="--", label="Impact Point")
plt.xlabel("Ground Distance (km)")
plt.ylabel("Altitude (m)")
plt.title("Ballistic Trajectory with Impact Point")
plt.legend()
plt.grid()
plt.xlim(0, impact_distance)  # Limit x-axis to impact distance
plt.show()

# Display impact information
print(f"Impact Time: {impact_time} seconds")
print(f"Impact Distance: {impact_distance} km")
