import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.widgets import Slider, Button
import yaml
import json
import os

# Load YAML config file
with open('config/map_config.yaml', 'r') as file:
    config = yaml.safe_load(file)

map_config = config['map_config']
simulation_settings = config['simulation_settings']
output_file = config['output_file']

# Load entity configuration file
with open('config/entity_config_guam_scenario.json', 'r') as f:
    entity_config = json.load(f)

# Check if the simulation output file exists
if not os.path.exists(output_file):
    raise FileNotFoundError(f"Output file {output_file} not found.")

# Read simulation output file
simulation_data = np.genfromtxt(output_file, delimiter=',', dtype=None, encoding='utf-8', names=True)

# Set up the figure and axis for dynamic resizing
fig, ax = plt.subplots(figsize=(8, 8))
plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.2)

# Set up Basemap with Mercator projection
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
times = simulation_data['time']
latitudes = simulation_data['lat']
longitudes = simulation_data['lon']

# Check if 'heading' field exists in the simulation data
if 'heading' in simulation_data.dtype.names:
    headings = simulation_data['heading']
else:
    headings = np.zeros(len(times))

entity_ids = simulation_data['entity']

# Initialize plot storage for each entity
entity_plots = {}
entity_labels = {}
leaderlines = {}

# Convert pixel dimensions to Mercator units
def pixels_to_merc_units(pixels, axis='x', fig=fig):
    if axis == 'x':
        delta_merc_x = m.urcrnrx - m.llcrnrx
        map_width_in_pixels = fig.get_size_inches()[0] * fig.dpi
        return pixels * delta_merc_x / map_width_in_pixels
    elif axis == 'y':
        delta_merc_y = m.urcrnry - m.llcrnry
        map_height_in_pixels = fig.get_size_inches()[1] * fig.dpi
        return pixels * delta_merc_y / map_height_in_pixels
    return 0

# Convert lat/lon to Mercator coordinates using Basemap
def latlon_to_merc(lon, lat):
    return m(lon, lat)

# Convert Mercator units to pixel units
def merc_units_to_pixels(merc_x, merc_y):
    """ Convert Mercator coordinates to pixel coordinates. """
    return ax.transData.transform((merc_x, merc_y))

# Check for label overlap (collision) in Mercator space
def check_collision(entity_id, label_x, label_y, label_w, label_h):
    """ Check for collision between labels in Mercator space. """
    print(f"Checking for collisions at Mercator position: ({label_x}, {label_y})")

    for other_entity_id, label in entity_labels.items():
        if other_entity_id == entity_id:
            continue  # Skip self comparison

        other_label_x, other_label_y = label.get_position()
        label_extent = label.get_window_extent(renderer=fig.canvas.get_renderer())
        other_label_w = pixels_to_merc_units(label_extent.width, axis='x')
        other_label_h = pixels_to_merc_units(label_extent.height, axis='y')

        print(f"Comparing against label for {other_entity_id}: Position ({other_label_x}, {other_label_y}), Width {other_label_w}, Height {other_label_h}")

        # Check for overlap in Mercator space
        if (abs(label_x - other_label_x) < (label_w + other_label_w) * 0.75) and \
           (abs(label_y - other_label_y) < (label_h + other_label_h) * 0.75):
            print(f"Collision detected with {other_entity_id}")
            return True

    return False

# Adjust label position if collision detected
def adjust_label_position(entity_id, label, label_x, label_y):
    """ Adjust the label position if a collision is detected. """
    print(f"Entity {entity_id} - Adjusting label to avoid collision")

    # Initial positions for shifting
    shift_x = pixels_to_merc_units(100, axis='x')
    shift_y = pixels_to_merc_units(100, axis='y')

    # Try shifting the label to avoid collision
    for _ in range(5):  # Try 5 different shifts
        new_label_x = label_x + shift_x
        new_label_y = label_y + shift_y

        label_extent = label.get_window_extent(renderer=fig.canvas.get_renderer())
        label_w = pixels_to_merc_units(label_extent.width, axis='x')
        label_h = pixels_to_merc_units(label_extent.height, axis='y')

        if not check_collision(entity_id, new_label_x, new_label_y, label_w, label_h):
            print(f"Entity {entity_id} - Moving label to ({new_label_x}, {new_label_y})")
            label.set_position((new_label_x, new_label_y))
            return new_label_x, new_label_y

        shift_x += pixels_to_merc_units(100, axis='x')
        shift_y += pixels_to_merc_units(100, axis='y')

    print(f"Entity {entity_id} - Collision couldn't be avoided, keeping at ({label_x}, {label_y})")
    return label_x, label_y

# Update label positions and leader lines
def update_labels_and_leaderlines():
    print("Updating labels and leaderlines...")
    for entity_id, label in entity_labels.items():
        label_x, label_y = label.get_position()
        label_x, label_y = adjust_label_position(entity_id, label, label_x, label_y)

        line = leaderlines[entity_id]
        icon_x, icon_y = entity_plots[entity_id].get_position()
        line.set_data([icon_x, label_x], [icon_y, label_y])

    plt.draw()

# Initialize entities on the map
for entity in entity_config['entities']:
    entity_id = entity['entity_id']
    
    render_info = entity.get('render', None)
    if render_info:
        lat = entity.get('lat', None)
        lon = entity.get('lon', None)

        if lon < map_config['llcrnrlon'] or lon > map_config['urcrnrlon'] or lat < map_config['llcrnrlat'] or lat > map_config['urcrnrlat']:
            print(f"Warning: Entity {entity_id} starts outside the map bounds.")

        if render_info.get('initial_render', False) or entity_id.encode() in entity_ids:
            x, y = latlon_to_merc(lon, lat)
            symbol = render_info.get('symbol', '!')
            color = render_info.get('color', 'blue')
            size = render_info.get('size', 10)

            entity_plots[entity_id] = plt.text(x, y, symbol, fontsize=size, color=color, ha='center', va='center', visible=True)

            label_offset = pixels_to_merc_units(50, axis='x')
            label_x, label_y = x + label_offset, y + label_offset
            entity_labels[entity_id] = ax.text(label_x, label_y, entity_id, ha='center', va='center')
            leaderlines[entity_id] = ax.plot([x, label_x], [y, label_y], 'k-')[0]

# Create slider and button
slider_min_time = int(np.min(times))
slider_max_time = int(np.max(times))
ax_slider = plt.axes([0.25, 0.08, 0.50, 0.03], facecolor='lightgoldenrodyellow')
time_slider = Slider(ax_slider, 'Time', slider_min_time, slider_max_time, valinit=slider_min_time, valfmt='%d')

ax_button_toggle = plt.axes([0.85, 0.02, 0.1, 0.04])
button_toggle = Button(ax_button_toggle, 'Labels')

# Function to update the plot based on time slider
def update_plot(current_time):
    total_time = slider_max_time
    time_slider.valtext.set_text(f"{int(current_time)}/{int(total_time)}")
    
    for entity_id, plot in entity_plots.items():
        entity_mask = (np.char.strip(simulation_data['entity'].astype(str)) == entity_id) & (simulation_data['time'] == current_time)
        
        if entity_mask.any():
            lat, lon = simulation_data['lat'][entity_mask][0], simulation_data['lon'][entity_mask][0]
            x, y = latlon_to_merc(lon, lat)
            
            if (map_config['llcrnrlon'] <= lon <= map_config['urcrnrlon'] and map_config['llcrnrlat'] <= lat <= map_config['urcrnrlat']):
                plot.set_position((x, y))

                label_offset = pixels_to_merc_units(50, axis='x')
                label_x, label_y = x + label_offset, y + label_offset
                print(f"Entity {entity_id} - Proposed position: ({label_x}, {label_y})")

                label_extent = entity_labels[entity_id].get_window_extent(renderer=fig.canvas.get_renderer())
                label_w, label_h = pixels_to_merc_units(label_extent.width, axis='x'), pixels_to_merc_units(label_extent.height, axis='y')

                if check_collision(entity_id, label_x, label_y, label_w, label_h):
                    label_x += label_offset * 0.5
                    print(f"Entity {entity_id} - Adjusting label to avoid collision: New position ({label_x}, {label_y})")

                entity_labels[entity_id].set_position((label_x, label_y))
                leaderlines[entity_id].set_data([x, label_x], [y, label_y])
                plot.set_visible(True)
            else:
                plot.set_visible(False)

    update_labels_and_leaderlines()

# Toggle label visibility
def toggle_labels(event=None):
    global show_labels
    show_labels = not show_labels
    for label in entity_labels.values():
        label.set_visible(show_labels)
    for line in leaderlines.values():
        line.set_visible(show_labels)
    plt.draw()

button_toggle.on_clicked(toggle_labels)

time_slider.on_changed(lambda val: update_plot(int(time_slider.val)))

plt.show()
