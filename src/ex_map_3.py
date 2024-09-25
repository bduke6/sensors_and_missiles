import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import yaml
from matplotlib.widgets import Slider, Button

# Load YAML config file
with open('config/map_config.yaml', 'r') as file:
    config = yaml.safe_load(file)

map_config = config['map_config']
simulation_settings = config['simulation_settings']

# Set up the figure and axis for dynamic resizing
fig, ax = plt.subplots(figsize=(8, 8))
plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.15)

# Set up Basemap
m = Basemap(projection=map_config['projection'],
            llcrnrlat=map_config['llcrnrlat'], urcrnrlat=map_config['urcrnrlat'],
            llcrnrlon=map_config['llcrnrlon'], urcrnrlon=map_config['urcrnrlon'],
            resolution=map_config['resolution'], ax=ax)

# Draw map details
m.drawcoastlines()
m.drawcountries()
m.drawparallels(np.arange(-90, 91, 10), labels=[1, 0, 0, 0])
m.drawmeridians(np.arange(-180, 181, 10), labels=[0, 0, 0, 1])

# Sample simulation data (to be replaced with real simulation data)
times = np.arange(0, simulation_settings['total_time'], simulation_settings['step_interval'])
latitudes = np.linspace(10, 20, len(times))  # Simulated latitude data
longitudes = np.linspace(105, 115, len(times))  # Simulated longitude data
headings = np.linspace(0, 360, len(times))  # Simulated heading data

# Initial plot for simulation (create empty placeholder for the airplane symbol)
x, y = m(longitudes[0], latitudes[0])
airplane_symbol = u'\u2708'  # Airplane symbol, could be any other symbol
airplane_text = plt.text(x, y, airplane_symbol, fontsize=20, rotation=headings[0], color='blue', ha='center', va='center', visible=False)

# Create the slider and button
ax_slider = plt.axes([0.25, 0.03, 0.50, 0.02], facecolor='lightgoldenrodyellow')
slider = Slider(ax_slider, 'Time', 0, len(times)-1, valinit=0, valfmt='%d')

ax_button_toggle = plt.axes([0.81, 0.025, 0.1, 0.04])
button_toggle = Button(ax_button_toggle, 'Run')

# State variable for controlling the simulation
is_running = False

def update_plot(val):
    """Update the map position and airplane symbol based on slider value."""
    t_index = int(slider.val)
    
    # Get current position
    current_lat = latitudes[t_index]
    current_lon = longitudes[t_index]
    
    # Convert lat/lon to map projection coordinates
    x, y = m(current_lon, current_lat)
    
    # Check if airplane is inside the map bounds
    if (map_config['llcrnrlon'] <= current_lon <= map_config['urcrnrlon'] and
        map_config['llcrnrlat'] <= current_lat <= map_config['urcrnrlat']):
        # Update airplane position and rotation
        airplane_text.set_position((x, y))  # Update position
        airplane_text.set_rotation(headings[t_index])  # Update rotation
        airplane_text.set_visible(True)  # Make visible if within bounds
    else:
        # Hide the airplane if out of bounds
        airplane_text.set_visible(False)

    plt.draw()

def toggle_simulation(event):
    """Toggle between running and stopping the simulation."""
    global is_running
    if is_running:
        # If running, stop the simulation
        is_running = False
        button_toggle.label.set_text('Run')
        plt.draw()  # Force a draw so the button label updates
    else:
        # If stopped, start the simulation
        is_running = True
        button_toggle.label.set_text('Stop')
        plt.draw()  # Force a draw so the button label updates
        run_simulation()

def run_simulation():
    """Run the simulation."""
    global is_running
    while is_running and slider.val < len(times)-1:
        slider.set_val(slider.val + 1)
        update_plot(slider.val)
        plt.pause(simulation_settings['step_interval'] / 10)  # Adjust for speed

def on_resize(event):
    """Handle window resizing to adjust map display."""
    fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.15)  # No need for tight_layout()
    plt.draw()

# Bind resize event to dynamically adjust layout
fig.canvas.mpl_connect('resize_event', on_resize)

# Event bindings
slider.on_changed(update_plot)
button_toggle.on_clicked(toggle_simulation)

# Display the map
plt.show()