import uuid
from calculations import geodetic_to_ecef, ecef_to_geodetic
import logging



class Entity:
    def __init__(self, lat, lon, alt, velocity, orientation, entity_id):
        self.lat = lat
        self.lon = lon
        self.alt = alt
        self.velocity = velocity  # Should be [0, 0, 0] for non-movable entities like ships
        self.orientation = orientation  # Orientation as [pitch, yaw, roll]
        self.entity_id = entity_id

    def move(self, time_step):
        # Update position based on velocity and time step
        self.lat += self.velocity[0] * time_step
        self.lon += self.velocity[1] * time_step
        self.alt += self.velocity[2] * time_step
        
        # Log the movement
        logging.info(f"Entity {self.entity_id} moved to lat: {self.lat}, lon: {self.lon}, alt: {self.alt}")

    def update_orientation(self, pitch_change=0, yaw_change=0, roll_change=0):
        # Update the orientation of the entity
        self.orientation[0] += pitch_change
        self.orientation[1] += yaw_change
        self.orientation[2] += roll_change

        # Ensure orientation stays within valid bounds (0-360 degrees for yaw, pitch, roll)
        self.orientation = [angle % 360 for angle in self.orientation]

        # Log the orientation change
        logging.info(f"Entity {self.entity_id} orientation updated to pitch: {self.orientation[0]}, yaw: {self.orientation[1]}, roll: {self.orientation[2]}")


class Ship(Entity):
    def __init__(self, lat, lon, alt, velocity, orientation, entity_id):
        super().__init__(lat, lon, alt, velocity, orientation, entity_id)
        # Ships typically have no acceleration, so they move at constant velocity if at all

    def launch(self, target):
        # Logic for launching a missile can go here
        logging.info(f"Ship {self.entity_id} launched a missile at {target.entity_id}")


class Missile(Entity):
    def __init__(self, lat, lon, alt, velocity, orientation, entity_id, fuel):
        super().__init__(lat, lon, alt, velocity, orientation, entity_id)
        self.fuel = fuel
        self.acceleration = [0, 0, 0]
        self.has_hit_ground = False

    def launch(self, target, environment):
        logging.info(f"Missile {self.entity_id} launched at target {target.entity_id}")
        
        # Set initial acceleration
        self.acceleration = [0, 0, 9.81]

        # Schedule the first move event
        self.schedule_movement_event(environment, time_step=0.1)

    def move(self, time_step, environment):
        if self.fuel > 0:
            # Update velocity based on acceleration while fuel remains
            for i in range(3):
                self.velocity[i] += self.acceleration[i] * time_step
            logging.info(f"Missile {self.entity_id} velocity: {self.velocity}")
            logging.info(f"Missile {self.entity_id} acceleration: {self.acceleration}")
            
            # Reduce fuel consumption based on time step
            self.fuel -= time_step * 10
            logging.info(f"Missile {self.entity_id} fuel remaining: {self.fuel}")

            if self.fuel <= 0:
                # When fuel runs out, switch to downward acceleration due to gravity
                self.acceleration = [0, 0, -9.81]
                logging.info(f"Missile {self.entity_id} ran out of fuel.")
        else:
            # Apply gravity after fuel is depleted
            self.velocity[2] += self.acceleration[2] * time_step  # Apply gravity to the vertical velocity
        
        super().move(time_step)

        # Check if the missile has hit the ground
        if self.alt <= 0:
            self.alt = 0
            self.has_hit_ground = True
            logging.info(f"Missile {self.entity_id} hit the ground.")
        else:
            self.schedule_movement_event(environment, time_step)

    def schedule_movement_event(self, environment, time_step):
        if not self.has_hit_ground:
            from events import MovementEvent
            next_event_time = environment.current_time + time_step
            environment.schedule_event(MovementEvent(next_event_time, self))



class Aircraft(Entity):
    def __init__(self, lat, lon, alt, velocity, orientation, entity_id=None):
        super().__init__(lat, lon, alt, velocity, orientation, entity_id)
        # Aircraft typically have more complex movement models but can use the default move logic

    def move(self, time_step):
        super().move(time_step)
        # Aircraft might experience more changes in orientation during movement
        self.update_orientation(pitch_change=2 * time_step, yaw_change=3 * time_step)  # Example pitch and yaw adjustments
