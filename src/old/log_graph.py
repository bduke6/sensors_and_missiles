import pandas as pd
import matplotlib.pyplot as plt
import re

def parse_log_file(log_file):
    timestamps = []
    altitudes = []
    latitudes = []
    longitudes = []
    
    with open(log_file, 'r') as file:
        for line in file:
            # Process lines that contain 'moved to', indicating a position update
            if 'moved to lat:' in line:
                # Extract the log line number as a stand-in for timestamp (since it's incremental)
                timestamp_match = re.match(r'(\d+) - ', line)
                altitude_match = re.search(r'alt: ([\-\d\.]+)', line)
                lat_match = re.search(r'lat: ([\d\.]+)', line)
                lon_match = re.search(r'lon: ([\d\.]+)', line)

                # Process and store data if available
                if timestamp_match and lat_match and lon_match and altitude_match:
                    timestamps.append(int(timestamp_match.group(1)))  # Use line number as a proxy for time
                    altitudes.append(float(altitude_match.group(1)))
                    latitudes.append(float(lat_match.group(1)))
                    longitudes.append(float(lon_match.group(1)))

    # Log summary of data
    print(f"Total data points processed: {len(timestamps)}")
    print(f"First 5 entries:")
    for i in range(min(5, len(timestamps))):
        print(f"Time: {timestamps[i]}, Lat: {latitudes[i]}, Lon: {longitudes[i]}, Alt: {altitudes[i]}")

    # Create DataFrame
    if len(timestamps) == len(altitudes) == len(latitudes) == len(longitudes):
        data = {
            'Timestamp': timestamps,
            'Altitude': altitudes,
            'Latitude': latitudes,
            'Longitude': longitudes
        }
        df = pd.DataFrame(data)
        return df
    else:
        raise ValueError("Mismatch in data lengths between timestamp, altitude, latitude, and longitude arrays.")
def plot_altitude_over_time(df):
    plt.figure()
    plt.plot(df['Timestamp'], df['Altitude'], label='Altitude', color='blue')
    plt.xlabel('Time (s)')
    plt.ylabel('Altitude (m)')
    plt.title('Altitude Over Time')
    plt.grid(True)
    plt.legend()
    plt.show()

def plot_location_with_padding(df):
    plt.figure()

    # Find the minimum and maximum values of latitude and longitude
    min_lat = df['Latitude'].min()
    max_lat = df['Latitude'].max()
    min_lon = df['Longitude'].min()
    max_lon = df['Longitude'].max()

    # Calculate the range for both latitude and longitude
    lat_range = max_lat - min_lat
    lon_range = max_lon - min_lon

    # Set padding by subtracting the range from the minimum to center the smallest value
    padded_lat = df['Latitude'] - (min_lat - lat_range)
    padded_lon = df['Longitude'] - (min_lon - lon_range)

    # Plot with padded latitude and longitude
    plt.scatter(padded_lon, padded_lat, c=df['Timestamp'], cmap='viridis', label='Missile Location', s=50)
    plt.colorbar(label='Time (s)')
    plt.xlabel('Longitude (Padded)')
    plt.ylabel('Latitude (Padded)')
    plt.title('Missile Location (Longitude vs Latitude, Padded)')
    plt.grid(True)
    plt.legend()
    plt.show()

def main():
    log_file = 'logs/entity.log'
    df = parse_log_file(log_file)
    
    # Plot altitude over time
    plot_altitude_over_time(df)
    
    # Plot location (latitude vs longitude)
    plot_location_with_padding(df)

if __name__ == '__main__':
    main()