import pymap3d as pm
import logging

logging.basicConfig(level=logging.INFO)

class MissileTrajectoryTester:
    def __init__(self, start_lat, start_lon, start_alt):
        self.start_lat = start_lat
        self.start_lon = start_lon
        self.start_alt = start_alt

        # Initial ECEF position
        self.start_x, self.start_y, self.start_z = pm.geodetic2ecef(
            self.start_lat, self.start_lon, self.start_alt
        )

    def neu_trajectory(self, up_velocity, time_step=1):
        """
        Simulate a north-up trajectory with ENU and convert to ECEF.
        """
        # Set North and Up components; East is zero for pure northward ascent
        north_velocity = up_velocity * 0.5  # Example north component
        up_component = up_velocity

        # Calculate ENU position
        e1 = 0  # East component is zero
        n1 = north_velocity * time_step  # North movement over time
        u1 = up_component * time_step  # Up movement over time

        # Convert ENU to ECEF
        x_ecef, y_ecef, z_ecef = pm.enu2ecef(
            e1, n1, u1, self.start_lat, self.start_lon, self.start_alt
        )

        return x_ecef, y_ecef, z_ecef

    def ecef_trajectory(self, elevation_angle, speed, time_step=1):
        """
        Directly apply ECEF movement using a high elevation angle.
        """
        azimuth = 0  # For simplicity, heading north
        x_vel, y_vel, z_vel = pm.aer2ecef(
            az=azimuth,
            el=elevation_angle,
            srange=speed * time_step,
            lat0=self.start_lat,
            lon0=self.start_lon,
            alt0=self.start_alt,
            deg=True
        )

        return x_vel, y_vel, z_vel

    def fixed_z_trajectory(self, fixed_z_velocity, time_step=1):
        """
        Simple trajectory with a fixed z velocity.
        """
        x_vel, y_vel = 0, 0  # Assume no lateral movement
        z_vel = fixed_z_velocity * time_step

        x_ecef = self.start_x + x_vel
        y_ecef = self.start_y + y_vel
        z_ecef = self.start_z + z_vel

        return x_ecef, y_ecef, z_ecef

# Instantiate tester
tester = MissileTrajectoryTester(start_lat=45.0, start_lon=-93.0, start_alt=0.0)

# Testing different trajectories
print("NEU Trajectory:", tester.neu_trajectory(up_velocity=1000))
print("ECEF Trajectory:", tester.ecef_trajectory(elevation_angle=90, speed=1000))
print("Fixed Z Trajectory:", tester.fixed_z_trajectory(fixed_z_velocity=1000))
