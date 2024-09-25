import os
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import yaml
import numpy as np
from mpl_toolkits.basemap import Basemap

# Load map configuration from YAML file
def load_map_config(file="./config/map_config.yaml"):  
    if os.path.exists(file):
        with open(file, 'r') as yaml_file:
            config = yaml.safe_load(yaml_file)
        return config
    else:
        print(f"Configuration file {file} not found!")
        return None

class MapViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulation Map Viewer")
        self.root.geometry("800x600")  # Set a smaller initial window size
        
        # Load map configuration
        self.config = load_map_config()
        if not self.config:
            print("Failed to load configuration. Exiting.")
            return
        
        # Access the map configuration inside 'map_config'
        map_config = self.config['map_config']
        simulation_settings = self.config['simulation_settings']
        
        self.simulation_data = None  # Holds simulation data
        
        # Set up Matplotlib figure and canvas
        self.fig, self.ax = plt.subplots(figsize=(8, 6))  # Adjust figure size for better layout
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Create Basemap instance using loaded config
        self.map = Basemap(
            projection=map_config['projection'],
            llcrnrlat=map_config['llcrnrlat'],
            urcrnrlat=map_config['urcrnrlat'],
            llcrnrlon=map_config['llcrnrlon'],
            urcrnrlon=map_config['urcrnrlon'],
            resolution=map_config['resolution'],
            ax=self.ax
        )
        self.map.drawcoastlines()
        self.map.drawcountries()
        
        # Add control buttons and slider
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)  # Ensure it stays below the map
        
        # Run/Stop button
        self.run_stop_button = tk.Button(self.control_frame, text="Run", command=self.toggle_simulation)
        self.run_stop_button.pack(side=tk.LEFT, padx=10)

        # Time step slider
        self.time_slider = tk.Scale(self.control_frame, from_=0, to=simulation_settings['total_time'], orient=tk.HORIZONTAL, label="Time Step")
        self.time_slider.pack(side=tk.LEFT, padx=10)
        
        # File selector button
        self.file_button = tk.Button(self.control_frame, text="Select Output File", command=self.select_output_file)
        self.file_button.pack(side=tk.LEFT, padx=10)

        # Simulation status
        self.simulation_running = False
        self.step_interval = simulation_settings['step_interval']

    def toggle_simulation(self):
        if self.simulation_running:
            self.simulation_running = False
            self.run_stop_button.config(text="Run")
        else:
            self.simulation_running = True
            self.run_stop_button.config(text="Stop")
            self.run_simulation()

    def select_output_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Simulation Output File",
            filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
        )
        if file_path:
            self.load_simulation_data(file_path)

    def load_simulation_data(self, file_path):
        # For demonstration, let's assume the simulation data is a CSV with lat/lon/time
        self.simulation_data = np.loadtxt(file_path, delimiter=',', skiprows=1)
        print(f"Loaded simulation data from {file_path}")

    def run_simulation(self):
        if self.simulation_data is None:
            print("No simulation data loaded.")
            return

        time_step = self.time_slider.get()
        latitudes = self.simulation_data[:, 0]
        longitudes = self.simulation_data[:, 1]
        
        # Clear the previous plot
        self.ax.clear()
        self.map.drawcoastlines()
        self.map.drawcountries()

        # Plot the simulation data up to the current time step
        for i in range(time_step + 1):
            x, y = self.map(longitudes[i], latitudes[i])
            self.map.plot(x, y, 'bo', markersize=5)

        # Update the canvas
        self.canvas.draw()

        # Continue the simulation loop if running
        if self.simulation_running and time_step < len(latitudes) - 1:
            self.root.after(int(self.step_interval * 1000), self.run_simulation)

# Main application setup
root = tk.Tk()
app = MapViewerApp(root)
root.mainloop()