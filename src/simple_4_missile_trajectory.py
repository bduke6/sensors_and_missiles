import numpy as np
import pymap3d.vincenty as vincenty
import matplotlib.pyplot as plt

# Constants
g = 9.81  # Gravity (m/s^2)
time_step = 1.0  # Time step in seconds

# Function to calculate the apogee and engine cutoff time
def calculate_apogee_and_cutoff(initial_velocity, launch_angle_deg):
    launch_angle_rad = np.radians(launch_angle_deg)
    
    # Time to reach apogee
    t_apogee = (initial_velocity * np.sin(launch_angle_rad)) / g
    
    # Apogee (highest altitude)
    apogee = (initial_velocity**2 * np.sin(launch_angle_rad)**2) / (2 * g)
    
    # Engine cutoff should happen before reaching apogee
    engine_cutoff_time = t_apogee * 0.9  # Set 90% of the time to apogee
    
    return apogee, engine_cutoff_time, t_apogee

# Function to calculate waypoints using vincenty.track2
def calculate_waypoints(lat1, lon1, lat2, lon2, npts=100):
    lats, lons = vincenty.track2(lat1, lon1, lat2, lon2, npts=npts)
    return lats, lons

# Simulating missile flight using waypoints and velocity vectors
def simulate_missile_flight(latitudes, longitudes, initial_velocity, engine_cutoff_time, flight_duration):
    t = 0.0
    powered_flight = True
    positions = []
    altitudes = []
    ground_distances = []
    engine_cutoff = False

    # Initial horizontal and vertical components of velocity (with thrust)
    launch_angle_rad = np.radians(45)
    v_horizontal = initial_velocity * np.cos(launch_angle_rad)
    v_vertical = initial_velocity * np.sin(launch_angle_rad)
    
    for i in range(len(latitudes)):
        if t >= flight_duration:
            break

        if t >= engine_cutoff_time:
            powered_flight = False
        
        # Calculate new position and velocity based on whether flight is powered
        if powered_flight:
            # Powered flight (with thrust)
            v_vertical -= g * time_step
        else:
            # Unpowered flight (ballistic trajectory)
            v_vertical -= g * time_step

        # Append the current lat, lon, and altitude
        positions.append((latitudes[i], longitudes[i]))
        
        # Simulate ballistic altitude profile
        altitude = (v_vertical * t) - (0.5 * g * t**2)
        altitudes.append(max(altitude, 0))  # Ensure altitude doesn't go negative

        # Calculate ground distance covered
        if i > 0:
            distance = vincenty.geodetic2aer(latitudes[i], longitudes[i], 0, latitudes[i-1], longitudes[i-1], 0)[2]
            ground_distances.append(ground_distances[-1] + distance if ground_distances else distance)

        t += time_step

        # Stop if the missile hits the ground (altitude < 0)
        if altitude <= 0:
            print("Missile hit the ground!")
            break

    return positions, altitudes, ground_distances

# Main function to run the simulation and plot results
def main():
    # Set initial velocity and launch angle
    initial_velocity = 7500  # Initial velocity in m/s
    launch_angle_deg = 45  # Launch angle in degrees
    flight_duration = 2000  # Extend flight duration to allow full descent

    # Calculate apogee and engine cutoff time
    apogee, engine_cutoff_time, t_apogee = calculate_apogee_and_cutoff(initial_velocity, launch_angle_deg)
    print(f"Apogee: {apogee:.2f} meters, Time to Apogee: {t_apogee:.2f} seconds, Engine Cutoff Time: {engine_cutoff_time:.2f} seconds")

    # Launch parameters (lat/lon for missile and target)
    start_lat, start_lon, start_alt = 5.0, 110.0, 0  # Launch point
    target_lat, target_lon, target_alt = 25.0, 120.5, 0  # Target point

    # Calculate waypoints using track2 function from pymap3d.vincenty
    latitudes, longitudes = calculate_waypoints(start_lat, start_lon, target_lat, target_lon, npts=100)

    # Simulate the missile's flight using waypoints
    positions, altitudes, ground_distances = simulate_missile_flight(
        latitudes, longitudes, initial_velocity, engine_cutoff_time, flight_duration)

    # Ensure there's data after the engine cutoff
    if len(ground_distances) > engine_cutoff_time:
        engine_cutoff_index = min(len(ground_distances) - 1, int(engine_cutoff_time // time_step))

        # Plot altitude profile with engine cutoff and unpowered flight marked
        plt.figure()
        
        # Plotting altitude over distance
        plt.plot(np.cumsum(ground_distances[:engine_cutoff_index]), altitudes[:engine_cutoff_index], color="blue", label="Missile Altitude Profile (Powered Flight)")
        plt.plot(np.cumsum(ground_distances[engine_cutoff_index:]), altitudes[engine_cutoff_index:], color="blue", linestyle="--", label="Missile Altitude Profile (Unpowered Flight)")
        
        plt.axvline(x=np.cumsum(ground_distances)[engine_cutoff_index], color="red", linestyle="--", label="Engine Cutoff")
        
        plt.xlabel("Ground Distance (meters)")
        plt.ylabel("Altitude (meters)")
        plt.title("Missile Altitude Profile Over Distance")
        plt.legend()
        plt.grid(True)
        plt.show()

        # Plot missile trajectory in lat/lon space
        lat_vals = [pos[0] for pos in positions]
        lon_vals = [pos[1] for pos in positions]

        plt.figure()
        plt.plot(lon_vals[:engine_cutoff_index], lat_vals[:engine_cutoff_index], color="green", label="Missile Trajectory (Powered Flight)")
        plt.plot(lon_vals[engine_cutoff_index:], lat_vals[engine_cutoff_index:], color="green", linestyle="--", label="Missile Trajectory (Unpowered Flight)")
        
        plt.scatter([start_lon], [start_lat], color="black", label="Launch Point", zorder=5)
        plt.scatter([target_lon], [target_lat], color="red", label="Target Point", zorder=5)
        plt.scatter([lon_vals[-1]], [lat_vals[-1]], color="blue", label="Impact Point", zorder=5)
        
        plt.axvline(x=lon_vals[engine_cutoff_index], color="red", linestyle="--", label="Engine Cutoff")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.title("Missile Flight Path in Lat/Lon")
        plt.legend()
        plt.grid(True)
        plt.show()
    else:
        print("Not enough data after engine cutoff.")

if __name__ == "__main__":
    main()
