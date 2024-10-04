import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.widgets import Slider
from ex_dla_2 import DynamicLabelAvoidance

# Set up the figure and axis for dynamic resizing
fig, ax = plt.subplots(figsize=(8, 8))
plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.2)

# Set up Basemap for the San Francisco Bay region
m = Basemap(projection='merc',
            llcrnrlat=37.5, urcrnrlat=38.5,
            llcrnrlon=-123.0, urcrnrlon=-121.5,
            resolution='h', ax=ax)

# Draw map details
m.drawcoastlines()
m.drawcountries()
m.drawstates()

# Initialize positions and velocities for 45 squares
num_squares = 45
x = np.random.rand(num_squares) * 0.5 - 123.0  # Random positions in lon range
y = np.random.rand(num_squares) * 1.0 + 37.5   # Random positions in lat range
vx = (np.random.rand(num_squares) - 0.5) * 0.01  # Random slow movement in lon
vy = (np.random.rand(num_squares) - 0.5) * 0.01  # Random slow movement in lat

# Labels for each square (entity_A, entity_B, etc.)
labels = [f"entity_{chr(65 + i % 26)}" for i in range(num_squares)]  # Labels A-Z, repeated

# Add squares and leader lines to the plot
squares = []
texts = []
lines = []

for i in range(num_squares):
    # Project lat/lon to Mercator x, y
    x_proj, y_proj = m(x[i], y[i])
    
    # Create square (rectangle) for each entity
    square = plt.Rectangle((x_proj, y_proj), 3000, 3000, fc='blue', zorder=5)
    ax.add_patch(square)
    squares.append(square)

    # Create label and leader line for each entity
    text = ax.text(x_proj, y_proj + 3000, labels[i], ha='center', va='bottom', zorder=10)
    texts.append(text)
    
    # Leader line from square to label
    line, = ax.plot([x_proj + 1500, x_proj + 1500], [y_proj + 3000, y_proj + 6000], 'k-', zorder=7)
    lines.append(line)

# Initialize DLA system (assuming this class is provided)
# Remove 'ax' from the DynamicLabelAvoidance initialization
dla = DynamicLabelAvoidance(icon_width=3000, icon_height=3000, line_gap=500)

# Add squares and labels to DLA
for i in range(num_squares):
    x_proj, y_proj = m(x[i], y[i])
    dla.add_entity(x_proj, y_proj)  # Remove the label argument

# Dictionary to store history of positions
history_dict = {}

# Function to keep squares in bounds
def keep_in_bounds(index, new_x, new_y):
    if new_x < m.llcrnrx:
        vx[index] *= -1
        new_x = m.llcrnrx
    elif new_x > m.urcrnrx - 3000:
        vx[index] *= -1
        new_x = m.urcrnrx - 3000
    if new_y < m.llcrnry:
        vy[index] *= -1
        new_y = m.llcrnry
    elif new_y > m.urcrnry - 3000:
        vy[index] *= -1
        new_y = m.urcrnry - 3000
    return new_x, new_y

# Function to update positions of squares and labels
def update_positions(current_time):
    if current_time not in history_dict:
        # Move squares and store current positions if not in history
        positions = []
        for j in range(num_squares):
            new_x = squares[j].get_x() + vx[j] * 1e6 * current_time / 100
            new_y = squares[j].get_y() + vy[j] * 1e6 * current_time / 100
            new_x, new_y = keep_in_bounds(j, new_x, new_y)

            positions.append((new_x, new_y))
            
            # Update square position
            squares[j].set_xy([new_x, new_y])

            # Get updated label and leader line positions from DLA
            label_x, label_y, leader_x_start, leader_y_start, leader_x_end, leader_y_end = dla.move_square(j, new_x, new_y)
            
            # Update label position
            texts[j].set_position((label_x, label_y))
            
            # Update leader line
            lines[j].set_data([leader_x_start, leader_x_end], [leader_y_start, leader_y_end])

        # Save positions for this time step
        history_dict[current_time] = positions
    else:
        # Revert to saved positions
        for j in range(num_squares):
            new_x, new_y = history_dict[current_time][j]
            squares[j].set_xy([new_x, new_y])

            # Get updated label and leader line positions from DLA
            label_x, label_y, leader_x_start, leader_y_start, leader_x_end, leader_y_end = dla.move_square(j, new_x, new_y)
            
            # Update label position
            texts[j].set_position((label_x, label_y))
            
            # Update leader line
            lines[j].set_data([leader_x_start, leader_x_end], [leader_y_start, leader_y_end])

    plt.draw()

# Slider for controlling the time progression
slider_min_time = 0
slider_max_time = 100
ax_slider = plt.axes([0.25, 0.02, 0.50, 0.03], facecolor='lightgoldenrodyellow')
time_slider = Slider(ax_slider, 'Time', slider_min_time, slider_max_time, valinit=slider_min_time, valfmt='%d')

# Link slider to plot update
time_slider.on_changed(lambda val: update_positions(int(val)))

# Display the plot
plt.show()