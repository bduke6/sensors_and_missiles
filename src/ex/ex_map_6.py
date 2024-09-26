import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import yaml
from matplotlib.widgets import Slider, Button
import os
import json

# Load YAML config file
with open('config/map_config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Extract the map and simulation settings
map_config = config['map_config']
simulation_settings = config['simulation_settings']
output_file = config['output_file']

# Load entity configuration file (for symbols, colors, etc.)
with open('config/entity_config_guam_scenario.json', 'r') as f:
    entity_config = json.load(f)

# Check if the simulation output file exists
if not os.path.exists(output_file):
    raise FileNotFoundError(f"Output file {output_file} not found.")

# Read the simulation output file
simulation_data = np.genfromtxt(output_file, delimiter=',', dtype=None, encoding='utf-8', names=True)

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

# Extract data from simulation file
times = simulation_data['time']  # Time from the simulation file
latitudes = simulation_data['lat']  # Latitudes from the file
longitudes = simulation_data['lon']  # Longitudes from the file

# Check if 'heading' field exists in the simulation data
if 'heading' in simulation_data.dtype.names:
    headings = simulation_data['heading']
else:
    headings = np.zeros(len(times))  # Default to 0 if heading data isn't available

entity_ids = simulation_data['entity']  # Entities from the file



# Initial plot for each entity based on entity configuration
entity_plots = {}

# Loop over the list of entities
for entity in entity_config['entities']:
    entity_id = entity['entity_id']
    
    # Get rendering details from the entity configuration
    render_info = entity.get('render', None)
    
    if render_info:
        # Get initial lat/lon for rendering entities without output data
        lat = entity.get('lat', None)
        lon = entity.get('lon', None)

        # Check if the entity is within the map bounds
        if lon < map_config['llcrnrlon'] or lon > map_config['urcrnrlon'] or lat < map_config['llcrnrlat'] or lat > map_config['urcrnrlat']:
            print(f"Warning: Entity {entity_id} starts outside the map bounds at ({lat}, {lon}). Map bounds: "
                    f"Latitude [{map_config['llcrnrlat']}, {map_config['urcrnrlat']}], "
                    f"Longitude [{map_config['llcrnrlon']}, {map_config['urcrnrlon']}].")
        
        # If the entity has an initial_render flag or simulation data, plot it
        if render_info.get('initial_render', False) or entity_id.encode() in entity_ids:
            x, y = m(lon, lat)
            symbol = render_info.get('symbol', '!')  # Default to '!' if no valid symbol is defined
            color = render_info.get('color', 'blue')  # Default to blue
            size = render_info.get('size', 10)  # Default size

            # Try to render as a text symbol first, fallback to '!' on error
            try:
                entity_plots[entity_id] = plt.text(x, y, symbol, fontsize=size, color=color, ha='center', va='center', visible=True)
            except Exception as e:
                print(f"Error with symbol {symbol} for entity {entity_id}: {e}")
                entity_plots[entity_id] = plt.text(x, y, '!', fontsize=size, color=color, ha='center', va='center', visible=True)

# Create the slider and button
ax_slider = plt.axes([0.25, 0.03, 0.50, 0.02], facecolor='lightgoldenrodyellow')
time_slider = Slider(ax_slider, 'Time', 0, len(times)-1, valinit=0, valfmt='%d')

ax_button_toggle = plt.axes([0.81, 0.025, 0.1, 0.04])
button_toggle = Button(ax_button_toggle, 'Run')

# State variable for controlling the simulation
is_running = False

def update_plot(val):
    """Update the map position and airplane symbol based on slider value."""
    t_index = int(time_slider.val)
    
    # Get current time
    current_time = times[t_index]

    for entity_id, plot in entity_plots.items():
        # Ensure entity_id in simulation_data is compared as a string
        entity_mask = (simulation_data['entity'].astype(str) == entity_id) & (simulation_data['time'] == current_time)
        if entity_mask.any():
            # Get current lat, lon, heading for the entity
            lat, lon = simulation_data['lat'][entity_mask][0], simulation_data['lon'][entity_mask][0]
            heading = simulation_data['heading'][entity_mask][0] if 'heading' in simulation_data.dtype.names else 0
            
            # Convert navigational heading to rotation for plotting (counterclockwise from x-axis)
            adjusted_heading = 90 - heading  # Convert navigational heading to map rotation
            
            x, y = m(lon, lat)
            
            # Check if the entity is within the map bounds
            if (map_config['llcrnrlon'] <= lon <= map_config['urcrnrlon'] and
                map_config['llcrnrlat'] <= lat <= map_config['urcrnrlat']):
                # Update entity position and rotation (for heading)
                plot.set_position((x, y))  # Update position for text symbols
                plot.set_rotation(adjusted_heading)  # Update rotation to match heading
                
                plot.set_visible(True)  # Make visible if within bounds
            else:
                # Hide the entity if it's out of bounds
                plot.set_visible(False)

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
    while is_running and time_slider.val < len(times)-1:
        time_slider.set_val(time_slider.val + 1)
        update_plot(time_slider.val)
        plt.pause(simulation_settings['step_interval'] / 10)  # Adjust for speed

def on_resize(event):
    """Handle window resizing to adjust map display."""
    fig.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.15)  # No need for tight_layout()
    plt.draw()

# Bind resize event to dynamically adjust layout
fig.canvas.mpl_connect('resize_event', on_resize)

# Event bindings
time_slider.on_changed(update_plot)
button_toggle.on_clicked(toggle_simulation)

# Display the map
plt.show()