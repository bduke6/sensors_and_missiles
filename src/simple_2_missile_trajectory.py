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

# Function to simulate missile flight and return data
def simulate_missile_flight(target_lat, target_lon, target_distance, initial_azimuth):
    altitudes = []
    ground_distances = []
    latitudes = []
    longitudes = []
    max_speed = 0

    # Adjust initial velocities based on the distance to the target
    horizontal_velocity = target_distance / (max_steps * time_step)  # Horizontal velocity in m/s
    initial_vertical_velocity = 5000 + (target_distance / 1000)  # Adjust vertical velocity

    up = 0  # Starting altitude
    distance_traveled = 0  # Ground distance along the great-circle path
    vertical_velocity = initial_vertical_velocity
    apogee_reached = False
    max_altitude = 0
    impact_time = None
    impact_distance = None

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

        altitudes.append(up)
        latitudes.append(lat)
        longitudes.append(lon)

        # Calculate horizontal ground distance in km
        ground_distance = distance_traveled / 1000
        ground_distances.append(ground_distance)

        # Calculate speed (magnitude of velocity)
        speed = math.sqrt(horizontal_velocity**2 + vertical_velocity**2)
        max_speed = max(max_speed, speed)

        # Check for impact (altitude at or below target altitude)
        if distance_traveled >= target_distance or up <= 0:
            impact_time = step * time_step
            impact_distance = ground_distance
            break

    launch_angle = calculate_launch_angle(initial_vertical_velocity, horizontal_velocity)
    strike_angle = calculate_strike_angle(vertical_velocity, horizontal_velocity)

    return altitudes, ground_distances, latitudes, longitudes, max_altitude, launch_angle, strike_angle, max_speed, impact_time, impact_distance

# Calculate the distances to the two targets
azimuth_1, target_distance_1 = calculate_great_circle_path(start_lat, start_lon, target_1_lat, target_1_lon)
azimuth_2, target_distance_2 = calculate_great_circle_path(start_lat, start_lon, target_2_lat, target_2_lon)

# Simulate both missiles
result_1 = simulate_missile_flight(target_1_lat, target_1_lon, target_distance_1, azimuth_1)
result_2 = simulate_missile_flight(target_2_lat, target_2_lon, target_distance_2, azimuth_2)

# Unpack results
altitudes_1, ground_distances_1, latitudes_1, longitudes_1, max_altitude_1, launch_angle_1, strike_angle_1, max_speed_1, impact_time_1, impact_distance_1 = result_1
altitudes_2, ground_distances_2, latitudes_2, longitudes_2, max_altitude_2, launch_angle_2, strike_angle_2, max_speed_2, impact_time_2, impact_distance_2 = result_2

# Plotting the ballistic trajectories for both missiles
plt.figure()
plt.plot(ground_distances_1, altitudes_1, color="blue", label="Missile 1 Altitude")
plt.plot(ground_distances_2, altitudes_2, color="green", label="Missile 2 Altitude")

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
plt.plot(longitudes_1, latitudes_1, color="blue", label="Missile 1 Track")
plt.plot(longitudes_2, latitudes_2, color="green", label="Missile 2 Track")
plt.scatter([start_lon], [start_lat], color="black", label="Launch Point", zorder=5)
plt.scatter([target_1_lon, target_2_lon], [target_1_lat, target_2_lat], color="red", label="Target Points", zorder=5)
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.title("Missile Flight Tracks on the Map")
plt.legend()
plt.grid()
plt.show()

# Print the flight characteristics
print(f"Missile 1 - Max Altitude: {max_altitude_1:.2f} m, Launch Angle: {launch_angle_1:.2f} degrees, Strike Angle: {strike_angle_1:.2f} degrees, Max Speed: {max_speed_1:.2f} m/s")
print(f"Missile 1 - Impact Time: {impact_time_1} seconds, Impact Distance: {impact_distance_1} km")

print(f"Missile 2 - Max Altitude: {max_altitude_2:.2f} m, Launch Angle: {launch_angle_2:.2f} degrees, Strike Angle: {strike_angle_2:.2f} degrees, Max Speed: {max_speed_2:.2f} m/s")
print(f"Missile 2 - Impact Time: {impact_time_2} seconds, Impact Distance: {impact_distance_2} km")
