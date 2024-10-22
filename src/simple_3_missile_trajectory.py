import pymap3d as pm
import matplotlib.pyplot as plt
import math

# Launch parameters
start_lat, start_lon, start_alt = 5.0, 110.0, 0  # Launch point (ground level)

# Target locations for two missiles
target_1_lat, target_1_lon, target_1_alt = 25.0, 120.5, 0  # Target 1 (ground level)
target_2_lat, target_2_lon, target_2_alt = 30.0, 130.0, 0  # Target 2 (ground level)

# Missile parameters
g = 9.81  # Gravity in m/s^2
time_step = 1  # Time step in seconds
max_steps = 5500  # Maximum number of simulation steps

# Function to calculate great-circle distance and initial bearing
def calculate_great_circle_path(lat1, lon1, lat2, lon2):
    # Use geodetic2aer to compute azimuth (initial bearing) and slant range (distance)
    azimuth, _, distance = pm.geodetic2aer(lat2, lon2, 0, lat1, lon1, 0, deg=True)
    return azimuth, distance

# Function to calculate launch angle
def calculate_launch_angle(vertical_velocity, horizontal_velocity):
    return math.degrees(math.atan(vertical_velocity / horizontal_velocity))

# Function to calculate strike angle
def calculate_strike_angle(vertical_velocity, horizontal_velocity):
    return math.degrees(math.atan(abs(vertical_velocity) / horizontal_velocity))

# Function to predict apogee and impact location based on initial conditions
def predict_apogee_impact(target_distance, initial_vertical_velocity):
    # Predicted apogee: where vertical velocity is zero
    apogee_altitude = initial_vertical_velocity**2 / (2 * g)
    
    # Predicted impact: horizontal distance equals target distance, altitude at 0
    return apogee_altitude, target_distance

# Function to simulate missile flight and return data
def simulate_missile_flight(target_lat, target_lon, target_distance, initial_azimuth, initial_vertical_velocity):
    altitudes = []
    ground_distances = []
    latitudes = []
    longitudes = []
    max_speed = 0

    # Adjust initial velocities based on the distance to the target
    horizontal_velocity = target_distance / (max_steps * time_step)  # Horizontal velocity in m/s

    up = 0  # Starting altitude
    distance_traveled = 0  # Ground distance along the great-circle path
    vertical_velocity = initial_vertical_velocity
    apogee_reached = False
    max_altitude = 0
    impact_time = None
    impact_distance = None

    ascent_points = {'ground_distances': [], 'altitudes': [], 'latitudes': [], 'longitudes': []}
    midcourse_points = {'ground_distances': [], 'altitudes': [], 'latitudes': [], 'longitudes': []}
    terminal_points = {'ground_distances': [], 'altitudes': [], 'latitudes': [], 'longitudes': []}

    # Simulate the ballistic trajectory
    for step in range(max_steps):
        if not apogee_reached:
            up += vertical_velocity * time_step
            vertical_velocity -= g * time_step  # Reduce vertical velocity due to gravity
            
            if vertical_velocity <= 0:
                apogee_reached = True
                max_altitude = up  # Record the apogee
                vertical_velocity = 0
        else:
            vertical_velocity -= g * time_step  # Gravity pulls missile down
            up += vertical_velocity * time_step

        # Horizontal movement along the great-circle path
        distance_traveled += horizontal_velocity * time_step
        if distance_traveled >= target_distance:
            distance_traveled = target_distance

        # Slant range: combine the horizontal distance and altitude to calculate it
        slant_range = math.sqrt(distance_traveled**2 + up**2)

        # Update the geodetic position (lat, lon) based on the current azimuth and slant range
        lat, lon, _ = pm.aer2geodetic(initial_azimuth, 0, slant_range, start_lat, start_lon, start_alt, deg=True)

        # Store data for plotting
        if not apogee_reached:
            ascent_points['ground_distances'].append(distance_traveled / 1000)
            ascent_points['altitudes'].append(up)
            ascent_points['latitudes'].append(lat)
            ascent_points['longitudes'].append(lon)
        elif vertical_velocity < -initial_vertical_velocity:
            midcourse_points['ground_distances'].append(distance_traveled / 1000)
            midcourse_points['altitudes'].append(up)
            midcourse_points['latitudes'].append(lat)
            midcourse_points['longitudes'].append(lon)
        else:
            terminal_points['ground_distances'].append(distance_traveled / 1000)
            terminal_points['altitudes'].append(up)
            terminal_points['latitudes'].append(lat)
            terminal_points['longitudes'].append(lon)

        # Check for impact (altitude at or below target altitude)
        if distance_traveled >= target_distance or up <= 0:
            impact_time = step * time_step
            impact_distance = distance_traveled / 1000
            break

    launch_angle = calculate_launch_angle(initial_vertical_velocity, horizontal_velocity)
    strike_angle = calculate_strike_angle(vertical_velocity, horizontal_velocity)

    return ascent_points, midcourse_points, terminal_points, max_altitude, launch_angle, strike_angle, max_speed, impact_time, impact_distance, lat, lon

# Calculate the distances to the two targets
azimuth_1, target_distance_1 = calculate_great_circle_path(start_lat, start_lon, target_1_lat, target_1_lon)
azimuth_2, target_distance_2 = calculate_great_circle_path(start_lat, start_lon, target_2_lat, target_2_lon)

# Initial velocities based on distance to the target
initial_vertical_velocity_1 = 5000 + (target_distance_1 / 1000)
initial_vertical_velocity_2 = 5000 + (target_distance_2 / 1000)

# Predict apogee and impact before the simulation
predicted_apogee_1, predicted_impact_1 = predict_apogee_impact(target_distance_1, initial_vertical_velocity_1)
predicted_apogee_2, predicted_impact_2 = predict_apogee_impact(target_distance_2, initial_vertical_velocity_2)

print(f"Predicted Missile 1 - Apogee Altitude: {predicted_apogee_1:.2f} m, Impact Distance: {predicted_impact_1 / 1000:.2f} km")
print(f"Predicted Missile 2 - Apogee Altitude: {predicted_apogee_2:.2f} m, Impact Distance: {predicted_impact_2 / 1000:.2f} km")

# Simulate both missiles
ascent_1, midcourse_1, terminal_1, max_altitude_1, launch_angle_1, strike_angle_1, max_speed_1, impact_time_1, impact_distance_1, impact_lat_1, impact_lon_1 = simulate_missile_flight(target_1_lat, target_1_lon, target_distance_1, azimuth_1, initial_vertical_velocity_1)
ascent_2, midcourse_2, terminal_2, max_altitude_2, launch_angle_2, strike_angle_2, max_speed_2, impact_time_2, impact_distance_2, impact_lat_2, impact_lon_2 = simulate_missile_flight(target_2_lat, target_2_lon, target_distance_2, azimuth_2, initial_vertical_velocity_2)

# Print post-simulation comparison with prediction
print(f"Missile 1 - Max Altitude: {max_altitude_1:.2f} m, Impact Distance: {impact_distance_1:.2f} km")
print(f"Missile 1 - Prediction Difference - Apogee Altitude: {abs(predicted_apogee_1 - max_altitude_1):.2f} m, Impact Distance: {abs(predicted_impact_1 / 1000 - impact_distance_1):.2f} km")

print(f"Missile 2 - Max Altitude: {max_altitude_2:.2f} m, Impact Distance: {impact_distance_2:.2f} km")
print(f"Missile 2 - Prediction Difference - Apogee Altitude: {abs(predicted_apogee_2 - max_altitude_2):.2f} m, Impact Distance: {abs(predicted_impact_2 / 1000 - impact_distance_2):.2f} km")

# Plotting the ballistic trajectories with different line styles
plt.figure()
# Missile 1
plt.plot(ascent_1['ground_distances'], ascent_1['altitudes'], color="blue", linestyle='-', label="Missile 1 Ascent")
plt.plot(midcourse_1['ground_distances'], midcourse_1['altitudes'], color="blue", linestyle='--', label="Missile 1 Midcourse")
plt.plot(terminal_1['ground_distances'], terminal_1['altitudes'], color="blue", linestyle=':', label="Missile 1 Terminal")

plt.axvline(x=impact_distance_1, color="red", linestyle="--", label="Missile 1 Impact")

# Missile 2
plt.plot(ascent_2['ground_distances'], ascent_2['altitudes'], color="green", linestyle='-', label="Missile 2 Ascent")
plt.plot(midcourse_2['ground_distances'], midcourse_2['altitudes'], color="green", linestyle='--', label="Missile 2 Midcourse")
plt.plot(terminal_2['ground_distances'], terminal_2['altitudes'], color="green", linestyle=':', label="Missile 2 Terminal")
plt.axvline(x=impact_distance_2, color="orange", linestyle="--", label="Missile 2 Impact")

plt.xlabel("Ground Distance (km)")
plt.ylabel("Altitude (m)")
plt.title("Missile Altitude over Distance for Two Targets")
plt.legend()
plt.grid()
plt.xlim(0, max(impact_distance_1, impact_distance_2))
plt.show()

# Simple map to show the flight tracks
plt.figure()
# Missile 1
plt.plot(ascent_1['longitudes'], ascent_1['latitudes'], color="blue", linestyle='-', label="Missile 1 Ascent")
plt.plot(midcourse_1['longitudes'], midcourse_1['latitudes'], color="blue", linestyle='--', label="Missile 1 Midcourse")
plt.plot(terminal_1['longitudes'], terminal_1['latitudes'], color="blue", linestyle=':', label="Missile 1 Terminal")

# Missile 2
plt.plot(ascent_2['longitudes'], ascent_2['latitudes'], color="green", linestyle='-', label="Missile 2 Ascent")
plt.plot(midcourse_2['longitudes'], midcourse_2['latitudes'], color="green", linestyle='--', label="Missile 2 Midcourse")
plt.plot(terminal_2['longitudes'], terminal_2['latitudes'], color="green", linestyle=':', label="Missile 2 Terminal")

plt.scatter([start_lon], [start_lat], color="black", label="Launch Point", zorder=5)
plt.scatter([target_1_lon, target_2_lon], [target_1_lat, target_2_lat], color="red", label="Target Points", zorder=5)
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Missile Flight Tracks on the Map")
plt.legend()
plt.grid()
plt.show()

# Print the flight characteristics
print(f"Missile 1 - Impact at Lat={impact_lat_1:.5f}, Lon={impact_lon_1:.5f}")
print(f"Missile 2 - Impact at Lat={impact_lat_2:.5f}, Lon={impact_lon_2:.5f}")

# Show prediction comparison for impact distance
print(f"Missile 1 - Distance from target: {target_distance_1 / 1000 - impact_distance_1:.2f} km")
print(f"Missile 2 - Distance from target: {target_distance_2 / 1000 - impact_distance_2:.2f} km")
