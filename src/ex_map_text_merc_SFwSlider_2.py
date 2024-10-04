import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.widgets import Slider

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
#labels = [chr(65 + i % 26) for i in range(num_squares)]  # Labels A-Z, repeated
labels = [f"entity_{chr(65 + i % 26)}" for i in range(num_squares)]  # Labels A-Z, repeated

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

# Function to calculate the scaling based on figure DPI and map extent
def calculate_scale_factor():
    # Get figure size and DPI
    fig_width_inch, fig_height_inch = fig.get_size_inches()  # Figure size in inches
    dpi = fig.get_dpi()  # Get the DPI (dots per inch)
    
    # Calculate figure size in pixels
    fig_width_px = fig_width_inch * dpi
    fig_height_px = fig_height_inch * dpi
    
    # Get map extents in map projection units (e.g., meters)
    map_width_m = m.urcrnrx - m.llcrnrx  # X-axis extent in map units
    map_height_m = m.urcrnry - m.llcrnry  # Y-axis extent in map units
    
    # Calculate the number of meters per pixel for both axes
    meters_per_pixel_x = map_width_m / fig_width_px
    meters_per_pixel_y = map_height_m / fig_height_px
    
    # For simplicity, we can average both dimensions
    meters_per_pixel = (meters_per_pixel_x + meters_per_pixel_y) / 2
    
    return meters_per_pixel

# Update square, label, and leader line positions
def update_plot(current_time):
    # Calculate the current scale factor based on the map magnification
    meters_per_pixel = calculate_scale_factor()

    # Set the desired width/height in pixels (e.g., 1000 pixels)
    icon_width_pixels = 50  # Desired square size in pixels
    label_width_pixels = 40  # Desired label width in pixels
    line_gap_pixels = 10  # Desired gap for leader line

    # Convert these pixel values to map units using meters_per_pixel
    icon_width = icon_width_pixels * meters_per_pixel
    icon_height = icon_width_pixels * meters_per_pixel
    fixed_label_w = label_width_pixels * meters_per_pixel
    fixed_label_h = 20 * meters_per_pixel  # Set label height
    line_gap = line_gap_pixels * meters_per_pixel  # Gap for leader line

    for j, square in enumerate(squares):
        # Move square
        new_x = square.get_x() + vx[j] * 1e6 * current_time / 100  # Multiply for a visible movement
        new_y = square.get_y() + vy[j] * 1e6 * current_time / 100
        new_x, new_y = keep_in_bounds(j, new_x, new_y)
        
        # Update square position
        square.set_xy([new_x, new_y])
        
        # Find non-overlapping position for the label
        label_x, label_y, pos = find_non_overlapping_position(j, new_x, new_y)
        
        # Update label position
        texts[j].set_position((label_x, label_y))
        
                # Simplify leader line to connect directly without two segments for now
        if pos == 'top':
            # Connect to bottom-center of the label
            lines[j].set_data([new_x + icon_width/2, label_x], [new_y + icon_height + line_gap, label_y - line_gap])
        elif pos == 'bottom':
            # Connect to top-center of the label
            lines[j].set_data([new_x + icon_width/2, label_x], [new_y - line_gap, label_y + fixed_label_h + line_gap])
        elif pos == 'left':
            # Connect to right-center of the label
            lines[j].set_data([new_x - line_gap, label_x + fixed_label_w/2 + line_gap ], [new_y + icon_height/2, label_y + fixed_label_h / 2])
        elif pos == 'right':
            # Connect to left-center of the label
            lines[j].set_data([new_x + icon_width - line_gap, label_x - fixed_label_w - line_gap], [new_y + icon_height/2, label_y + fixed_label_h / 2])
        
    plt.draw()
# Slider for controlling the time progression
slider_min_time = 0
slider_max_time = 100
ax_slider = plt.axes([0.25, 0.02, 0.50, 0.03], facecolor='lightgoldenrodyellow')
time_slider = Slider(ax_slider, 'Time', slider_min_time, slider_max_time, valinit=slider_min_time, valfmt='%d')

# Link slider to plot update
time_slider.on_changed(lambda val: update_plot(int(val)))

# Display the plot
plt.show()