class DynamicLabelAvoidance:
    def __init__(self, icon_width, icon_height, line_gap):
        # Store bounding box dimensions and spacing
        self.icon_width = icon_width
        self.icon_height = icon_height
        self.line_gap = line_gap
        
        # Track positions for squares, labels, and leader lines
        self.squares = []
        self.texts = []
        self.lines = []
    
    def add_entity(self, x_proj, y_proj, label):
        """Adds a new entity (square, label, and leader line) to be tracked."""
        square = {'x': x_proj, 'y': y_proj, 'width': self.icon_width, 'height': self.icon_height}
        text = {'x': x_proj, 'y': y_proj + self.icon_height, 'label': label}
        line = {'x1': x_proj + self.icon_width / 2, 'y1': y_proj + self.icon_height + self.line_gap,
                'x2': x_proj + self.icon_width / 2, 'y2': y_proj + self.icon_height + self.line_gap}
        
        # Store the square, label, and leader line in internal lists
        self.squares.append(square)
        self.texts.append(text)
        self.lines.append(line)
    
    def move_square(self, index, new_x, new_y):
        """Updates the square's position and returns the new label position."""
        square = self.squares[index]
        square['x'] = new_x
        square['y'] = new_y

        # Find the new position for the label to avoid overlaps
        label_x, label_y, pos = self.find_non_overlapping_position(index, new_x, new_y)

        # Update leader line information
        self.update_leader_line(index, new_x, new_y, label_x, label_y, pos)

        return label_x, label_y

    def find_non_overlapping_position(self, index, new_x, new_y):
        """Finds a position for the label that avoids collisions with other labels."""
        positions = ['top', 'bottom', 'left', 'right']
        for pos in positions:
            if pos == 'top':
                proposed_x, proposed_y = new_x + self.icon_width / 2, new_y + self.icon_height + 2000
            elif pos == 'bottom':
                proposed_x, proposed_y = new_x + self.icon_width / 2, new_y - 2000
            elif pos == 'left':
                proposed_x, proposed_y = new_x - 2000, new_y + self.icon_height / 2
            elif pos == 'right':
                proposed_x, proposed_y = new_x + self.icon_width + 2000, new_y + self.icon_height / 2

            # Check for collisions with other squares
            collision = False
            for j, other_square in enumerate(self.squares):
                if j != index:
                    other_x, other_y = other_square['x'], other_square['y']
                    if (proposed_x >= other_x - self.icon_width and proposed_x <= other_x + self.icon_width and
                        proposed_y >= other_y - self.icon_height and proposed_y <= other_y + self.icon_height):
                        collision = True
                        break

            if not collision:
                return proposed_x, proposed_y, pos
        
        # Default to placing the label above if no other position is found
        return new_x + self.icon_width / 2, new_y + self.icon_height + 2000, 'top'

    def update_leader_line(self, index, new_x, new_y, label_x, label_y, pos):
        """Updates the leader line position based on the square and label positions."""
        line = self.lines[index]
        if pos == 'top':
            line['x1'], line['y1'] = new_x + self.icon_width / 2, new_y + self.icon_height + self.line_gap
            line['x2'], line['y2'] = label_x, label_y - self.line_gap
        elif pos == 'bottom':
            line['x1'], line['y1'] = new_x + self.icon_width / 2, new_y - self.line_gap
            line['x2'], line['y2'] = label_x, label_y + self.line_gap + self.icon_height
        elif pos == 'left':
            line['x1'], line['y1'] = new_x - self.line_gap, new_y + self.icon_height / 2
            line['x2'], line['y2'] = label_x + self.line_gap + self.line_gap, label_y + self.icon_height / 2
        elif pos == 'right':
            line['x1'], line['y1'] = new_x + self.icon_width + self.line_gap, new_y + self.icon_height / 2
            line['x2'], line['y2'] = label_x - self.line_gap, label_y + self.icon_height / 2

        # # Simplify leader line to connect directly without two segments for now
        # if pos == 'top':
        #     # Connect to bottom-center of the label
        #     lines[j].set_data([new_x + icon_width/2, label_x], [new_y + icon_height + line_gap, label_y - line_gap])
        # elif pos == 'bottom':
        #     # Connect to top-center of the label
        #     lines[j].set_data([new_x + icon_width/2, label_x], [new_y - line_gap, label_y + fixed_label_h + line_gap])
        # elif pos == 'left':
        #     # Connect to right-center of the label
        #     lines[j].set_data([new_x - line_gap, label_x + fixed_label_w/2 + line_gap ], [new_y + icon_height/2, label_y + fixed_label_h / 2])
        # elif pos == 'right':
        #     # Connect to left-center of the label
        #     lines[j].set_data([new_x + icon_width + line_gap, label_x - line_gap], [new_y + icon_height/2, label_y + fixed_label_h / 2])
        

    def get_square_positions(self):
        """Returns the current positions of all squares."""
        return [(square['x'], square['y']) for square in self.squares]