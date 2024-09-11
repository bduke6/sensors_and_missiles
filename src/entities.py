import uuid
from calculations import geodetic_to_ecef, ecef_to_geodetic
import logging
from events import MovementEvent  # Import needed event classes

# Create a logger for entities
entity_logger = logging.getLogger('entity')

class Entity:
    def __init__(self, lat, lon, alt, velocity, orientation, entity_id=None):
        # Convert geodetic to ECEF
        self.X, self.Y, self.Z = geodetic_to_ecef(lat, lon, alt)
        self.velocity = velocity  # Should be [vx, vy, vz] for movement in ECEF
        self.orientation = orientation  # Orientation as [pitch, yaw, roll]
        self.entity_id = entity_id or str(uuid.uuid4())
        self.has_hit_ground = False

    def move(self, time_step, env):  # Added 'env' parameter here
        # Update ECEF position based on velocity and time step
        self.X += self.velocity[0] * time_step
        self.Y += self.velocity[1] * time_step
        self.Z += self.velocity[2] * time_step

        # Convert back to geodetic for logging or external use
        lat, lon, alt = ecef_to_geodetic(self.X, self.Y, self.Z)
        entity_logger.info(f"Entity {self.entity_id} moved to ECEF ({self.X}, {self.Y}, {self.Z})")
        entity_logger.info(f"Entity {self.entity_id} moved to lat: {lat}, lon: {lon}, alt: {alt}")

        # Check if the entity has hit the ground
        if alt <= 0:
            self.Z = 0  # Stop movement at ground level
            self.has_hit_ground = True
            entity_logger.info(f"Entity {self.entity_id} hit the ground.")
        else:
            # Schedule the next movement event
            self.schedule_event("MovementEvent", env, time_step)

    def update_orientation(self, pitch_change=0, yaw_change=0, roll_change=0):
        # Update the orientation of the entity
        self.orientation[0] += pitch_change
        self.orientation[1] += yaw_change
        self.orientation[2] += roll_change

        # Ensure orientation stays within valid bounds (0-360 degrees for yaw, pitch, roll)
        self.orientation = [angle % 360 for angle in self.orientation]

        # Log the orientation change
        entity_logger.info(f"Entity {self.entity_id} orientation updated to pitch: {self.orientation[0]}, "
                           f"yaw: {self.orientation[1]}, roll: {self.orientation[2]}")

    def handle_event(self, event, env):  # Changed parameter to 'env'
        """Handle the event that this entity is affected by."""
        if isinstance(event, MovementEvent):
            self.move(event.time_step, env)  # Pass 'env' to the move function

    def schedule_event(self, event_type, env, time_step):  # Changed parameter to 'env'
        """Schedule an event for this entity."""
        if hasattr(env, 'current_time'):
            next_event_time = env.current_time + time_step
            env.schedule_event(MovementEvent(next_event_time, self, time_step))
        else:
            raise AttributeError("The environment object does not have 'current_time'")

class Ship(Entity):
    def __init__(self, lat, lon, alt, velocity, orientation, entity_id=None):
        super().__init__(lat, lon, alt, velocity, orientation, entity_id)
        # Ships typically have no acceleration, so they move at constant velocity if at all

    def launch(self, target, env):  # Changed 'environment' to 'env'
        # Logic for launching a missile
        entity_logger.info(f"Ship {self.entity_id} launched a missile at {target.entity_id}")

class Missile(Entity):
    def __init__(self, lat, lon, alt, velocity, orientation, entity_id=None, fuel=100):
        super().__init__(lat, lon, alt, velocity, orientation, entity_id)
        self.fuel = fuel
        self.acceleration = [0, 0, 0]

    def launch(self, target, env):  # Changed 'environment' to 'env'
        entity_logger.info(f"Missile {self.entity_id} launched at target {target.entity_id}")

        # Set initial acceleration
        self.acceleration = [0, 0, 9.81]

        # Schedule the first move event
        self.schedule_event("MovementEvent", env, time_step=0.1)

    def move(self, time_step, env):  # Added 'env' parameter here
        if self.fuel > 0:
            # Update velocity based on acceleration while fuel remains
            for i in range(3):
                self.velocity[i] += self.acceleration[i] * time_step

            #Tesing to see if the logger is working
            entity_logger.debug(f"Testing entity_logger for Missile {self.entity_id}")
            entity_logger.info(f"Missile {self.entity_id} velocity: {self.velocity}")
            entity_logger.info(f"Missile {self.entity_id} acceleration: {self.acceleration}")

            # Reduce fuel consumption based on time step
            self.fuel -= time_step * 10
            entity_logger.info(f"Missile {self.entity_id} fuel remaining: {self.fuel}")

            if self.fuel <= 0:
                # When fuel runs out, switch to downward acceleration due to gravity
                self.acceleration = [0, 0, -9.81]
                entity_logger.info(f"Missile {self.entity_id} ran out of fuel.")
        else:
            # Apply gravity after fuel is depleted
            self.velocity[2] += self.acceleration[2] * time_step  # Apply gravity to the vertical velocity

        super().move(time_step, env)  # Pass 'env' to the move function, logs from Entity will be used

class Aircraft(Entity):
    def __init__(self, lat, lon, alt, velocity, orientation, entity_id=None):
        super().__init__(lat, lon, alt, velocity, orientation, entity_id)
        # Aircraft typically have more complex movement models but can use the default move logic

    def move(self, time_step, env):  # Added 'env' parameter here
        super().move(time_step, env)  # Pass 'env' to the move function
        # Aircraft might experience more changes in orientation during movement
        self.update_orientation(pitch_change=2 * time_step, yaw_change=3 * time_step)  # Example pitch and yaw adjustments
