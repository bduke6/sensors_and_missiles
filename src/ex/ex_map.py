import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import yaml
from matplotlib.widgets import Slider, Button
import time

# Load YAML config file
with open('config/map_config.yaml', 'r') as file:
    config = yaml.safe_load(file)

map_config = config['map_config']
simulation_settings = config['simulation_settings']

# Set up Basemap
m = Basemap(projection=map_config['projection'],
            llcrnrlat=map_config['llcrnrlat'], urcrnrlat=map_config['urcrnrlat'],
            llcrnrlon=map_config['llcrnrlon'], urcrnrlon=map_config['urcrnrlon'],
            resolution=map_config['resolution'])

# Draw map details
m.drawcoastlines()
m.drawcountries()
m.drawparallels(np.arange(-90, 91, 10), labels=[1, 0, 0, 0])
m.drawmeridians(np.arange(-180, 181, 10), labels=[0, 0, 0, 1])

# Sample simulation data (to be replaced with real simulation data)
times = np.arange(0, simulation_settings['total_time'], simulation_settings['step_interval'])
latitudes = np.linspace(10, 20, len(times))  # Simulated latitude data
longitudes = np.linspace(105, 115, len(times))  # Simulated longitude data

# Initial plot for simulation
x, y = m(longitudes[0], latitudes[0])
point, = m.plot(x, y, 'bo', markersize=10)

# Create the slider and buttons
ax_slider = plt.axes([0.25, 0.03, 0.50, 0.02], facecolor='lightgoldenrodyellow')
slider = Slider(ax_slider, 'Time', 0, len(times)-1, valinit=0, valfmt='%d')

ax_button_run = plt.axes([0.81, 0.025, 0.1, 0.04])
button_run = Button(ax_button_run, 'Run')

ax_button_stop = plt.axes([0.91, 0.025, 0.1, 0.04])
button_stop = Button(ax_button_stop, 'Stop')

is_running = False

def update_plot(val):
    """Update the map position based on slider value."""
    t_index = int(slider.val)
    x, y = m(longitudes[t_index], latitudes[t_index])
    point.set_data(x, y)
    plt.draw()

def run_simulation(event):
    """Start simulation."""
    global is_running
    is_running = True
    while is_running and slider.val < len(times)-1:
        slider.set_val(slider.val + 1)
        update_plot(slider.val)
        plt.pause(simulation_settings['step_interval'] / 10)  # Adjust for speed

def stop_simulation(event):
    """Stop simulation."""
    global is_running
    is_running = False

# Event bindings
slider.on_changed(update_plot)
button_run.on_clicked(run_simulation)
button_stop.on_clicked(stop_simulation)

# Display the map
plt.show()