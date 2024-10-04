class DynamicLabelAvoidance:
    def __init__(self, icon_width, icon_height, line_gap):
        self.icon_width = icon_width
        self.icon_height = icon_height
        self.label_width = 2000
        self.label_height = 400
        self.line_gap = line_gap
        self.squares = []  # List of dictionaries representing each square's position and bounding box.

    def add_entity(self, x_proj, y_proj):
        """Adds a new entity with its bounding box."""
        square = {'x': x_proj, 'y': y_proj, 'width': self.icon_width, 'height': self.icon_height}
        self.squares.append(square)

    def move_square(self, index, new_x, new_y):
        """Updates the position of the square and checks for label collisions."""
        # Update the square's position
        self.squares[index]['x'] = new_x
        self.squares[index]['y'] = new_y

        # Get label and leader line positions (with collision avoidance)
        label_x, label_y, pos = self.find_non_overlapping_position(index, new_x, new_y)

        # Calculate leader line start and end points
        leader_x_start, leader_y_start, leader_x_end, leader_y_end = self.update_leader_line(index, new_x, new_y, label_x, label_y, pos)

        # Return the updated label position and leader line positions for rendering
        return label_x, label_y, leader_x_start, leader_y_start, leader_x_end, leader_y_end

    def find_non_overlapping_position(self, index, new_x, new_y):
        """Detects collisions with other entities and finds a non-overlapping label position."""
        positions = ['top', 'bottom', 'left', 'right']
        for pos in positions:
            proposed_x, proposed_y = new_x, new_y
            if pos == 'top':
                proposed_x, proposed_y = new_x + self.icon_width / 2, new_y + self.icon_height + 2000
            elif pos == 'bottom':
                proposed_x, proposed_y = new_x + self.icon_width / 2, new_y - 2000
            elif pos == 'left':
                proposed_x, proposed_y = new_x - 2000, new_y + self.icon_height / 2
            elif pos == 'right':
                proposed_x, proposed_y = new_x + self.icon_width + 2000, new_y + self.icon_height / 2
            
            # Check for collisions with other entities
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

        # Default to top position if no other works
        return new_x + self.icon_width / 2, new_y + self.icon_height + 2000, 'top'

    def update_leader_line(self, index, new_x, new_y, label_x, label_y, pos):
        """Calculates the leader line's start and end positions based on label position."""
        if pos == 'top':
            leader_x_start = new_x + self.icon_width / 2
            leader_y_start = new_y + self.icon_height + self.line_gap
            leader_x_end = label_x
            leader_y_end = label_y - self.line_gap
        elif pos == 'bottom':
            leader_x_start = new_x + self.icon_width / 2
            leader_y_start = new_y - self.line_gap
            leader_x_end = label_x
            leader_y_end = label_y + self.label_height + self.line_gap
        elif pos == 'left':
            leader_x_start = new_x - self.line_gap
            leader_y_start = new_y + self.icon_height / 2
            leader_x_end = label_x + self.line_gap
            leader_y_end = label_y + self.icon_height / 2
        elif pos == 'right':
            leader_x_start = new_x + self.icon_width + self.line_gap
            leader_y_start = new_y + self.icon_height / 2
            leader_x_end = label_x - self.line_gap
            leader_y_end = label_y + self.icon_height / 2
        
        return leader_x_start, leader_y_start, leader_x_end, leader_y_end