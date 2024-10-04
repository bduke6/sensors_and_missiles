import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.widgets import Slider
import matplotlib.animation as animation

# Set up the figure and axis for dynamic resizing
fig, ax = plt.subplots()
plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.15)

# Set up Basemap with Mercator projection
m = Basemap(projection='merc', llcrnrlat=10, urcrnrlat=50,
            llcrnrlon=-130, urcrnrlon=-60, resolution='l', ax=ax)
m.drawcoastlines()

# Initialize positions and velocities for 15 squares (lat, lon for geographic realism)
num_squares = 15
lat = np.random.uniform(15, 45, num_squares)  # Latitude between 15 and 45 degrees
lon = np.random.uniform(-120, -80, num_squares)  # Longitude between -120 and -80 degrees
vx = (np.random.rand(num_squares) - 0.5) * 0.1  # Slow movement in lat
vy = (np.random.rand(num_squares) - 0.5) * 0.1  # Slow movement in lon
labels = [chr(65 + i) for i in range(num_squares)]  # Labels A, B, C, ..., O

# Create squares, labels, and leader lines (converted to map projection coordinates)
squares = []
texts = []
lines = []

for i in range(num_squares):
    x, y = m(lon[i], lat[i])  # Project to map coordinates
    square = plt.Rectangle((x, y), 50000, 50000, fc='blue')  # Adjust square size
    squares.append(square)
    ax.add_patch(square)
    text = ax.text(x, y + 100000, labels[i], ha='center', va='bottom', fontsize=10)
    texts.append(text)
    line, = ax.plot([x, x], [y + 50000, y + 100000], 'k-')
    lines.append(line)

# Define possible label positions (top, bottom, left, right)
positions = ['top', 'bottom', 'left', 'right']

# Function to check bounds and reverse velocity
def keep_in_bounds(index, new_lon, new_lat):
    if new_lon < -120 or new_lon > -80:
        vx[index] *= -1  # Reverse direction
        new_lon = np.clip(new_lon, -120, -80)
    if new_lat < 15 or new_lat > 45:
        vy[index] *= -1
        new_lat = np.clip(new_lat, 15, 45)
    return new_lon, new_lat

# Function to find non-overlapping label position
def find_non_overlapping_position(index, new_x, new_y):
    for pos in positions:
        proposed_x, proposed_y = new_x, new_y
        if pos == 'top':
            proposed_x, proposed_y = new_x, new_y + 120000
        elif pos == 'bottom':
            proposed_x, proposed_y = new_x, new_y - 80000
        elif pos == 'left':
            proposed_x, proposed_y = new_x - 100000, new_y
        elif pos == 'right':
            proposed_x, proposed_y = new_x + 100000, new_y

        # Check for collisions
        collision = False
        for j, square in enumerate(squares):
            if j != index:
                other_x, other_y = square.get_xy()
                if (proposed_x >= other_x - 50000 and proposed_x <= other_x + 50000 and
                        proposed_y >= other_y - 50000 and proposed_y <= other_y + 50000):
                    collision = True
                    break
        if not collision:
            return proposed_x, proposed_y, pos
    return new_x, new_y + 120000, 'top'

# Function to update the positions of squares, labels, and leader lines
def update_plot(current_time):
    for i, square in enumerate(squares):
        # Convert back to lat/lon, update and re-project
        new_lon = lon[i] + vx[i]
        new_lat = lat[i] + vy[i]
        new_lon, new_lat = keep_in_bounds(i, new_lon, new_lat)
        x, y = m(new_lon, new_lat)

        # Update square
        square.set_xy([x, y])

        # Find non-overlapping label position
        label_x, label_y, pos = find_non_overlapping_position(i, x, y)

        # Update label and leader lines
        texts[i].set_position((label_x, label_y))
        if pos == 'top':
            lines[i].set_data([x + 25000, label_x], [y + 50000, label_y - 50000])
        elif pos == 'bottom':
            lines[i].set_data([x + 25000, label_x], [y, label_y + 50000])
        elif pos == 'left':
            lines[i].set_data([x, label_x + 50000], [y + 25000, label_y])
        elif pos == 'right':
            lines[i].set_data([x + 50000, label_x - 50000], [y + 25000, label_y])

        # Update the lat/lon for the next iteration
        lon[i], lat[i] = new_lon, new_lat

    plt.draw()

# Create a slider to control the animation (time progression)
slider_min_time = 0
slider_max_time = 100
ax_slider = plt.axes([0.25, 0.02, 0.50, 0.03], facecolor='lightgoldenrodyellow')
time_slider = Slider(ax_slider, 'Time', slider_min_time, slider_max_time, valinit=slider_min_time, valfmt='%d')

# Function to animate the entities
def animate(i):
    update_plot(i)
    return squares + texts + lines

# Create animation
ani = animation.FuncAnimation(fig, animate, frames=100, interval=50)

# Bind the slider to update the plot
time_slider.on_changed(lambda val: update_plot(int(val)))

plt.show()