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
initial_velocity = 7500  # Standard initial missile velocity in m/s

# Convert launch and target coordinates to ECEF
start_ecef = pm.geodetic2ecef(start_lat, start_lon, start_alt)
target_1_ecef = pm.geodetic2ecef(target_1_lat, target_1_lon, target_1_alt)
target_2_ecef = pm.geodetic2ecef(target_2_lat, target_2_lon, target_2_alt)

# Function to calculate great-circle distance using ECEF
def calculate_great_circle_path_ecef(start_ecef, target_ecef):
    distance = math.sqrt((target_ecef[0] - start_ecef[0])**2 + 
                         (target_ecef[1] - start_ecef[1])**2 + 
                         (target_ecef[2] - start_ecef[2])**2)
    return distance

# Function to calculate launch angle
def calculate_launch_angle(vertical_velocity, horizontal_velocity):
    return math.degrees(math.atan(vertical_velocity / horizontal_velocity))

# Function to calculate strike angle
def calculate_strike_angle(vertical_velocity, horizontal_velocity):
    return math.degrees(math.atan(abs(vertical_velocity) / horizontal_velocity))

# Function to calculate initial velocities based on the launch angle
def calculate_initial_velocities(initial_velocity, launch_angle_deg):
    launch_angle_rad = math.radians(launch_angle_deg)
    vertical_velocity = initial_velocity * math.sin(launch_angle_rad)
    horizontal_velocity = initial_velocity * math.cos(launch_angle_rad)
    return vertical_velocity, horizontal_velocity

# Function to predict apogee and impact using ECEF
def predict_apogee_impact_ecef(target_distance, initial_velocity):
    g = 9.81
    sin2theta = (target_distance * g) / (initial_velocity ** 2)
    
    if sin2theta > 1:
        raise ValueError("Target is beyond maximum range")
    
    theta = math.asin(sin2theta) / 2
    initial_vertical_velocity = initial_velocity * math.sin(theta)
    apogee = (initial_vertical_velocity ** 2) / (2 * g)
    return apogee, target_distance

# Function to simulate missile flight using ECEF coordinates
def simulate_missile_flight_ecef(target_ecef, initial_velocity):
    ascent_points = {'ground_distances': [], 'altitudes': [], 'latitudes': [], 'longitudes': []}
    midcourse_points = {'ground_distances': [], 'altitudes': [], 'latitudes': [], 'longitudes': []}
    terminal_points = {'ground_distances': [], 'altitudes': [], 'latitudes': [], 'longitudes': []}

    max_altitude = 0
    start_ecef = pm.geodetic2ecef(start_lat, start_lon, start_alt)
    current_ecef = list(start_ecef)
    
    # Calculate initial launch parameters
    target_distance = calculate_great_circle_path_ecef(start_ecef, target_ecef)
    apogee, _ = predict_apogee_impact_ecef(target_distance, initial_velocity)
    
    # Simulate the missile flight in time steps
    for step in range(max_steps):
        horizontal_velocity = initial_velocity  # Horizontal velocity is assumed constant
        vertical_velocity = initial_velocity - (g * step * time_step)
        altitude = (initial_velocity * step * time_step) - (0.5 * g * (step * time_step) ** 2)
        
        # Calculate position in ECEF based on the missile's velocity
        x = current_ecef[0] + horizontal_velocity * time_step
        y = current_ecef[1] + vertical_velocity * time_step
        z = altitude
        
        current_ecef = [x, y, z]
        lat, lon, _ = pm.ecef2geodetic(*current_ecef)
        
        # Store ascent, midcourse, and terminal phase data
        if vertical_velocity > 0:
            ascent_points['ground_distances'].append(step * time_step)
            ascent_points['altitudes'].append(altitude)
            ascent_points['latitudes'].append(lat)
            ascent_points['longitudes'].append(lon)
        elif vertical_velocity <= 0 and altitude > 0:
            midcourse_points['ground_distances'].append(step * time_step)
            midcourse_points['altitudes'].append(altitude)
            midcourse_points['latitudes'].append(lat)
            midcourse_points['longitudes'].append(lon)
        else:
            terminal_points['ground_distances'].append(step * time_step)
            terminal_points['altitudes'].append(altitude)
            terminal_points['latitudes'].append(lat)
            terminal_points['longitudes'].append(lon)
        
        if altitude <= 0:
            break
        
        # Track the maximum altitude
        if altitude > max_altitude:
            max_altitude = altitude
    
    impact_distance = step * time_step
    return ascent_points, midcourse_points, terminal_points, max_altitude, impact_distance, lat, lon

# Calculate the distances to the two targets using ECEF
target_distance_1 = calculate_great_circle_path_ecef(start_ecef, target_1_ecef)
target_distance_2 = calculate_great_circle_path_ecef(start_ecef, target_2_ecef)

# Predict apogee and impact before the simulation
predicted_apogee_1, predicted_impact_1 = predict_apogee_impact_ecef(target_distance_1, initial_velocity)
predicted_apogee_2, predicted_impact_2 = predict_apogee_impact_ecef(target_distance_2, initial_velocity)

print(f"Predicted Missile 1 - Apogee Altitude: {predicted_apogee_1:.2f} m")
print(f"Predicted Missile 2 - Apogee Altitude: {predicted_apogee_2:.2f} m")

# Simulate both missiles using ECEF coordinates
ascent_1, midcourse_1, terminal_1, max_altitude_1, impact_distance_1, impact_lat_1, impact_lon_1 = simulate_missile_flight_ecef(target_1_ecef, initial_velocity)
ascent_2, midcourse_2, terminal_2, max_altitude_2, impact_distance_2, impact_lat_2, impact_lon_2 = simulate_missile_flight_ecef(target_2_ecef, initial_velocity)

# Print post-simulation results
print(f"Missile 1 - Max Altitude: {max_altitude_1:.2f} m, Impact Distance: {impact_distance_1:.2f} km")
print(f"Missile 1 - Impact at Lat={impact_lat_1:.5f}, Lon={impact_lon_1:.5f}")

print(f"Missile 2 - Max Altitude: {max_altitude_2:.2f} m, Impact Distance: {impact_distance_2:.2f} km")
print(f"Missile 2 - Impact at Lat={impact_lat_2:.5f}, Lon={impact_lon_2:.5f}")

# Plot the results
plt.figure()
plt.plot(ascent_1['ground_distances'], ascent_1['altitudes'], color="blue", label="Missile 1 Ascent")
plt.plot(midcourse_1['ground_distances'], midcourse_1['altitudes'], color="blue", linestyle='--', label="Missile 1 Midcourse")
plt.plot(terminal_1['ground_distances'], terminal_1['altitudes'], color="blue", linestyle=':', label="Missile 1 Terminal")

plt.plot(ascent_2['ground_distances'], ascent_2['altitudes'], color="green", label="Missile 2 Ascent")
plt.plot(midcourse_2['ground_distances'], midcourse_2['altitudes'], color="green", linestyle='--', label="Missile 2 Midcourse")
plt.plot(terminal_2['ground_distances'], terminal_2['altitudes'], color="green", linestyle=':', label="Missile 2 Terminal")

plt.axvline(x=impact_distance_1, color="red", linestyle="--", label="Missile 1 Impact")
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