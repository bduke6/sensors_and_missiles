import os
import glob
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import math

# Helper function to calculate distance between two lat/lon points using the Haversine formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c  # Distance in kilometers

# Helper function to find the latest file matching the base filename
def find_latest_log_file(base_filename, logs_dir='logs'):
    """Find the latest file with a given base filename in the specified directory."""
    pattern = os.path.join(logs_dir, f"*{base_filename}*.csv")  # Adjust to match CSV files
    files = glob.glob(pattern)
    
    if not files:
        raise FileNotFoundError(f"No file found matching pattern {pattern}")

    latest_file = max(files, key=os.path.getmtime)
    print(f"Found latest file: {latest_file}")
    return latest_file

# Function to read CSV and plot altitude over distance
def plot_altitude_over_distance(file_path):
    data = pd.read_csv(file_path)
    data = data[data['entity'] == 'missile_1']  # Filter for missile_1
    
    # Calculate ground distance flown using successive lat/lon
    distances = [0]  # Starting point with zero distance
    total_distance = 0

    for i in range(1, len(data)):
        lat1, lon1 = data.iloc[i - 1][['lat', 'lon']]
        lat2, lon2 = data.iloc[i][['lat', 'lon']]
        dist = haversine(lat1, lon1, lat2, lon2)
        total_distance += dist
        distances.append(total_distance)

    data['distance'] = distances

    # Plot altitude over ground distance
    plt.plot(data['distance'], data['alt'], color="blue", label="Missile 1 Altitude")
    plt.xlabel("Distance Flown (km)")
    plt.ylabel("Altitude (m)")
    plt.title("Missile 1 Altitude over Distance")
    plt.legend()
    plt.grid()
    plt.show()

# Main script execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot altitude vs distance from simulation data.")
    parser.add_argument('--latest', help="Base name to search for the latest file", required=True)
    args = parser.parse_args()

    # Find the latest file based on provided base name
    file_path = find_latest_log_file(args.latest)
    plot_altitude_over_distance(file_path)
