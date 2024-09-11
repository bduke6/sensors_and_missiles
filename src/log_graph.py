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
            # Extract the timestamp, altitude, latitude, and longitude
            timestamp_match = re.match(r'(\d+\.\d+) - ', line)
            altitude_match = re.search(r'alt: ([\-\d\.]+)', line)
            lat_match = re.search(r'lat: ([\d\.]+)', line)
            lon_match = re.search(r'lon: ([\d\.]+)', line)

            # Show what's happening in the log processing
            print(f"Processing line: {line.strip()}")
            if timestamp_match:
                print(f"Found timestamp: {timestamp_match.group(1)}")
            if lat_match and lon_match and altitude_match:
                print(f"Found lat: {lat_match.group(1)}, lon: {lon_match.group(1)}, alt: {altitude_match.group(1)}")

            if timestamp_match and lat_match and lon_match and altitude_match:
                # Append only if all values are present
                timestamps.append(float(timestamp_match.group(1)))
                altitudes.append(float(altitude_match.group(1)))
                latitudes.append(float(lat_match.group(1)))
                longitudes.append(float(lon_match.group(1)))

            else:
                print(f"Skipping line due to missing data.")

    # Check if lists are of equal length
    print(f"Final list sizes: timestamps={len(timestamps)}, altitudes={len(altitudes)}, latitudes={len(latitudes)}, longitudes={len(longitudes)}")
    
    if len(timestamps) == len(altitudes) == len(latitudes) == len(longitudes):
        # Create a pandas DataFrame for easier manipulation
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
    plt.plot(df['Timestamp'], df['Altitude'], label='Altitude')
    plt.xlabel('Time (s)')
    plt.ylabel('Altitude (m)')
    plt.title('Altitude Over Time')
    plt.legend()
    plt.show()

def plot_location(df):
    plt.figure()
    plt.scatter(df['Latitude'], df['Longitude'], c=df['Timestamp'], cmap='viridis', label='Missile Location')
    plt.colorbar(label='Time (s)')
    plt.xlabel('Latitude')
    plt.ylabel('Longitude')
    plt.title('Missile Location (Latitude vs Longitude)')
    plt.legend()
    plt.show()

def main():
    log_file = 'logs/entity.log'  # Adjusted to the correct log file path
    df = parse_log_file(log_file)
    
    # Plot altitude over time
    plot_altitude_over_time(df)
    
    # Plot location (latitude vs longitude)
    plot_location(df)

if __name__ == '__main__':
    main()
