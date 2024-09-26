import matplotlib.pyplot as plt

def load_coastline_data(file_path):
    """Load coastline data from a text file."""
    latitudes = []
    longitudes = []
    
    with open(file_path, 'r') as file:
        for line in file:
            try:
                lat, lon = map(float, line.split())
                latitudes.append(lat)
                longitudes.append(lon)
            except ValueError:
                # Skip any malformed lines
                continue
    
    return latitudes, longitudes

def plot_cartesian_grid_with_land(coastline_file):
    # Create a figure and axis
    fig, ax = plt.subplots()

    # Set grid lines and labels
    ax.grid(True)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')

    # Load coastline data from the text file
    coastline_lat, coastline_lon = load_coastline_data(coastline_file)

    # Plot the coastline with grey points instead of lines
    ax.scatter(coastline_lon, coastline_lat, s=1, color='grey')  # 's' controls point size

    # Plot the point for Nanjing
    nanjing_x, nanjing_y = 118.8, 32
    ax.plot(nanjing_x, nanjing_y, marker='o', color='red', label="Nanjing")
    ax.text(nanjing_x, nanjing_y, '  Nanjing', fontsize=12, verticalalignment='bottom', color='red')

    # Plot Dalian
    dalian_x, dalian_y = 121.6, 39.0
    ax.plot(dalian_x, dalian_y, marker='o', color='red', label="Dalian")
    ax.text(dalian_x, dalian_y, '  Dalian', fontsize=12, verticalalignment='bottom', color='red')

    # Plot CSG Reagan
    csg_reagan_x, csg_reagan_y = 140.0, 31.0
    ax.plot(csg_reagan_x, csg_reagan_y, marker='o', color='blue', label="CSG Reagan")
    ax.text(csg_reagan_x, csg_reagan_y, '  CSG Reagan', fontsize=12, verticalalignment='bottom', color='blue')

    # Set limits for better visibility
    ax.set_xlim(115, 145)
    ax.set_ylim(30, 45)

    # Set the title
    ax.set_title('Map with Coastlines and Key Points')

    # Show the plot
    plt.show()

def main():
    # Define the path to the coastline file
    coastline_file = 'data/30-115--45-145-asia-cil.txt'  # Replace with your actual file path
    plot_cartesian_grid_with_land(coastline_file)

if __name__ == "__main__":
    main()
