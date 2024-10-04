import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.widgets import Slider
import matplotlib.animation as animation

# Set up the figure and axis for dynamic resizing
fig, ax = plt.subplots(figsize=(8, 8))
plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.2)

# Set up Basemap for the San Francisco Bay region
m = Basemap(projection='merc',
            llcrnrlat=37.5, urcrnrlat=38.5,
            llcrnrlon=-123.0, urcrnrlon=-121.5,
            resolution='h', ax=ax)

m.drawcoastlines()
m.drawcountries()
m.drawstates()

# Initialize positions and velocities for 45 squares
num_squares = 45
x = np.random.rand(num_squares) * 0.5 - 123.0  # Random positions in lon range
y = np.random.rand(num_squares) * 1.0 + 37.5   # Random positions in lat range
vx = (np.random.rand(num_squares) - 0.5) * 0.01  # Random slow movement in lon
vy = (np.random.rand(num_squares) - 0.5) * 0.01  # Random slow movement in lat
labels = [chr(65 + i % 26) for i in range(num_squares)]  # Labels A-Z, repeated

# Convert initial lat/lon to map (mercator) coordinates
squares = []
texts = []
lines = []

# Add squares, labels, and leader lines to the plot
for i in range(num_squares):
    x_proj, y_proj = m(x[i], y[i])
    square = plt.Rectangle((x_proj, y_proj), 3000, 3000, fc='blue', zorder=5)
    text = ax.text(x_proj, y_proj + 3000, labels[i], ha='center', va='bottom', zorder=10)
    line, = ax.plot([x_proj + 1500, x_proj + 1500], [y_proj + 3000, y_proj + 6000], 'k-', zorder=7)
    
    squares.append(square)
    texts.append(text)
    lines.append(line)
    ax.add_patch(square)

# Define possible label positions (top, bottom, left, right)
positions = ['top', 'bottom', 'left', 'right']

# Keep square in bounds and reverse velocity on collision with map edges
def keep_in_bounds(index, new_x, new_y):
    if new_x < m.llcrnrx:
        vx[index] *= -1  # Reverse direction
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

# Detect label collisions and find a position that avoids overlap
def find_non_overlapping_position(index, new_x, new_y):
    for pos in positions:
        proposed_x, proposed_y = new_x, new_y
        if pos == 'top':
            proposed_x, proposed_y = new_x + 1500, new_y + 6000  # Offset label further from square
        elif pos == 'bottom':
            proposed_x, proposed_y = new_x + 1500, new_y - 3000
        elif pos == 'left':
            proposed_x, proposed_y = new_x - 6000, new_y + 1500
        elif pos == 'right':
            proposed_x, proposed_y = new_x + 6000, new_y + 1500
        
        # Check for collisions with other labels and squares
        collision = False
        for j, other_square in enumerate(squares):
            if j != index:
                other_x, other_y = other_square.get_x(), other_square.get_y()
                if (proposed_x >= other_x - 3000 and proposed_x <= other_x + 3000 and
                    proposed_y >= other_y - 3000 and proposed_y <= other_y + 3000):
                    collision = True
                    break
        
        if not collision:
            return proposed_x, proposed_y, pos
    return new_x + 1500, new_y + 6000, 'top'  # Default to top if no other position works

# Update square, label, and leader line positions
def update_plot(current_time):
    for j, square in enumerate(squares):
        # Move square
        new_x = square.get_x() + vx[j] * 1e6  # Multiply for a visible movement
        new_y = square.get_y() + vy[j] * 1e6
        new_x, new_y = keep_in_bounds(j, new_x, new_y)
        
        # Update square position
        square.set_xy([new_x, new_y])
        
        # Find non-overlapping position for the label
        label_x, label_y, pos = find_non_overlapping_position(j, new_x, new_y)
        
        # Update label position
        texts[j].set_position((label_x, label_y))
        
        # Update leader line (from square side to label)
        if pos == 'top':
            lines[j].set_data([new_x + 1500, new_x + 1500, label_x], [new_y + 3000, new_y + 6000, label_y])
        elif pos == 'bottom':
            lines[j].set_data([new_x + 1500, new_x + 1500, label_x], [new_y, new_y - 3000, label_y])
        elif pos == 'left':
            lines[j].set_data([new_x, new_x - 3000, label_x], [new_y + 1500, new_y + 1500, label_y])
        elif pos == 'right':
            lines[j].set_data([new_x + 3000, new_x + 6000, label_x], [new_y + 1500, new_y + 1500, label_y])

    plt.draw()

# Slider for controlling the time progression
slider_min_time = 0
slider_max_time = 100
ax_slider = plt.axes([0.25, 0.02, 0.50, 0.03], facecolor='lightgoldenrodyellow')
time_slider = Slider(ax_slider, 'Time', slider_min_time, slider_max_time, valinit=slider_min_time, valfmt='%d')

# Animation function to update plot continuously
def animate(i):
    update_plot(i)
    return squares + texts + lines

# Create animation
ani = animation.FuncAnimation(fig, animate, frames=100, interval=500)

# Link slider to plot update
time_slider.on_changed(lambda val: update_plot(int(val)))

# Display the plot
plt.show()