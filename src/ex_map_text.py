import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import matplotlib.animation as animation

# Set up the figure and axis
fig, ax = plt.subplots()
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)

# Initialize positions and velocities for 15 squares
num_squares = 15
x = np.random.rand(num_squares) * 9
y = np.random.rand(num_squares) * 9
vx = (np.random.rand(num_squares) - 0.5) * 0.2  # Slow movement
vy = (np.random.rand(num_squares) - 0.5) * 0.2
labels = [chr(65 + i) for i in range(num_squares)]  # Labels A, B, C, ..., O

# Create squares, labels, and leader lines
squares = [plt.Rectangle((x[i], y[i]), 0.5, 0.5, fc='blue') for i in range(num_squares)]
texts = [ax.text(x[i], y[i] + 1, labels[i], ha='center', va='bottom') for i in range(num_squares)]
lines = [ax.plot([x[i] + 0.25, x[i] + 0.25], [y[i] + 0.5, y[i] + 1], 'k-')[0] for i in range(num_squares)]

# Add squares to the plot
for square in squares:
    ax.add_patch(square)

# Define possible label positions (top, bottom, left, right)
positions = ['top', 'bottom', 'left', 'right']

# Function to keep squares within bounds and reverse velocity on collision
def keep_in_bounds(index, new_x, new_y):
    if new_x < 0:
        vx[index] *= -1  # Reverse direction
        new_x = 0
    elif new_x > 9.5:
        vx[index] *= -1
        new_x = 9.5
    if new_y < 0:
        vy[index] *= -1
        new_y = 0
    elif new_y > 9.5:
        vy[index] *= -1
        new_y = 9.5
    return new_x, new_y

# Function to calculate new label position that doesn't overlap with other labels or squares
def find_non_overlapping_position(index, new_x, new_y):
    for pos in positions:
        proposed_x, proposed_y = new_x, new_y
        if pos == 'top':
            proposed_x, proposed_y = new_x + 0.25, new_y + 1.2  # Offset label further from square
        elif pos == 'bottom':
            proposed_x, proposed_y = new_x + 0.25, new_y - 1
        elif pos == 'left':
            proposed_x, proposed_y = new_x - 1.2, new_y + 0.25
        elif pos == 'right':
            proposed_x, proposed_y = new_x + 1.2, new_y + 0.25
        
        # Check for collisions with other labels and squares
        collision = False
        for j, other_square in enumerate(squares):
            if j != index:
                other_x, other_y = other_square.get_x(), other_square.get_y()
                if (proposed_x >= other_x - 0.75 and proposed_x <= other_x + 1.25 and
                    proposed_y >= other_y - 0.75 and proposed_y <= other_y + 1.25):
                    collision = True
                    break
        
        if not collision:
            return proposed_x, proposed_y, pos
    return new_x + 0.25, new_y + 1.2, 'top'  # Default position is top if no other works

# Function to update the positions of the squares, labels, and leader lines based on the current time (slider value)
def update_plot(current_time):
    for j, square in enumerate(squares):
        # Move square
        new_x = square.get_x() + vx[j]
        new_y = square.get_y() + vy[j]
        new_x, new_y = keep_in_bounds(j, new_x, new_y)  # Keep within bounds
        
        # Update square position
        square.set_xy([new_x, new_y])
        
        # Find non-overlapping position for the label
        label_x, label_y, pos = find_non_overlapping_position(j, new_x, new_y)
        
        # Update label position
        texts[j].set_position((label_x, label_y))
        
        # Update leader line (from square side to label)
        if pos == 'top':
            lines[j].set_data([new_x + 0.25, new_x + 0.25, label_x], [new_y + 0.5, new_y + 1, label_y + 0.01])
        elif pos == 'bottom':
            # Connect leader line to the top of the label when it's below the square
            lines[j].set_data([new_x + 0.25, new_x + 0.25, label_x], [new_y, new_y - 0.5, label_y + 0.5])
        elif pos == 'left':
            lines[j].set_data([new_x, new_x - 0.5, label_x], [new_y + 0.25, new_y + 0.25, label_y])
        elif pos == 'right':
            lines[j].set_data([new_x + 0.5, new_x + 1, label_x], [new_y + 0.25, new_y + 0.25, label_y])

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

# Display the plot
plt.show()
