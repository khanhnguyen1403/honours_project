from tkinter import *
from tkinter import messagebox as msgbox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import datetime
import random
import time
from datetime import datetime, timedelta
import matplotlib.dates as mdates

class RootGUI: 
    def __init__(self):
        self.root = Tk()
        self.root.title("DC Nanogrid Control Panel")
        self.root.geometry("800x480")
        self.root.resizable(False, False)
        self.root.config(bg="white")

        self.root.grid_rowconfigure(4, weight=1)
        self.root.grid_columnconfigure(6, weight=2)


class RandomValueGenerator: #testing purposes
    def __init__(self):
        self.base_values = {}  #store base values
        self.variation_ranges = {}  #store variation ranges
    
    def set_appliance_parameters(self, appliance_name, base_power, variation_percent=5):
        """Set base power and variation range for an appliance"""
        self.base_values[appliance_name] = base_power
        variation = base_power * (variation_percent / 100)
        self.variation_ranges[appliance_name] = variation
    
    def generate_value(self, appliance_name, is_on=True):
        if not is_on:
            return 0
            
        if appliance_name not in self.base_values:
            return 0
            
        base = self.base_values[appliance_name]
        variation = self.variation_ranges[appliance_name]
        
        # Generate random value within variation range
        min_val = max(0, base - variation)
        max_val = base + variation
        
        return round(random.uniform(min_val, max_val), 1)
    
    def generate_summary_values(self, appliances_dict):
        """Generate summary values for the 'All' appliance"""
        total_consumption = 0
        total_generation = 0
        
        for name, appliance in appliances_dict.items():
            if name == "All" or appliance is None:
                continue
                
            if appliance.type == 0 and appliance.power_status:  # Load
                total_consumption += self.generate_value(name, appliance.power_status)
            elif appliance.type == 1 and appliance.power_status:  # Source
                total_generation += self.generate_value(name, appliance.power_status)
        
        return total_consumption, total_generation


class Appliance:
    def __init__(self, name, ID):
        self.name = name
        self.power_status = False
        self.ID = ID
        
        # Initialize all possible properties
        self.type = 0  # 0: load, 1: source, 2: storage
        self.voltage_rating = 0
        self.power_rating = 0
        self.power = [0] * 300  # Array of 300 elements for power values
        self.voltage = 0
        self.current = 0
        self.time_operated = 0 # in seconds
        self.energy_used = 0  # kWh
        self.fault = False
        
        # Additional properties for different appliance types
        # Load properties
        self.max_current = 0
        self.overvoltage_threshold = 0
        self.undervoltage_threshold = 0
        self.differential_threshold = 0
        
        # Source properties
        self.max_output_power = 0
        self.max_output_current = 0
        
        # Storage properties
        self.capacity = 0
        self.max_charge_current = 0
        self.max_discharge_current = 0
        
        # Tracking variables
        self.power_on_time = 0  # Track time when appliance is on
        self.last_update_time = time.time()

    def update_power_value(self, new_power_value):
        # Shift all values left by one position
        self.power[:-1] = self.power[1:]
        # Add new value at the end
        self.power[-1] = new_power_value
        
        # Update time operated if appliance is on
        current_time = time.time()
        if self.power_status:
            self.power_on_time += (current_time - self.last_update_time)
            self.time_operated = int(self.power_on_time)
            
            # Update energy used (simplified calculation)
            # Energy = Power * Time (in kWh)
            self.energy_used += (new_power_value * (current_time - self.last_update_time)) / 3600000  # Convert to kWh
        
        self.last_update_time = current_time

    def get_current_power(self): #instantaneous power 
        return self.power[-1]

    def get_power_history(self): #return the array
        return self.power.copy()

    # MISSING METHODS - ADD THESE:
    def properties(self):
        """Return all properties as a dictionary"""
        return {
            'name': self.name,
            'type': self.type,
            'power_status': self.power_status,
            'voltage_rating': self.voltage_rating,
            'power_rating': self.power_rating,
            'current_power': self.get_current_power(),
            'voltage': self.voltage,
            'current': self.current,
            'energy_used': self.energy_used,
            'time_operated': self.time_operated,
            'fault': self.fault
        }

    def toggle_power(self):
        if self.power_status:
            self.power_status = False
        else:
            self.power_status = True
            # Reset timing when turned on
            self.last_update_time = time.time()

    def get_status_text(self):
        return "ON" if self.power_status else "OFF"
    
    def get_status_color(self):
        return 'green' if self.power_status else 'red'

    def get_power_consumption(self):
        """Get current power consumption (for loads)"""
        if self.type == 0 and self.power_status:  # Load type and ON
            return self.get_current_power()
        return 0

    def get_power_generation(self):
        """Get current power generation (for sources)"""
        if self.type == 1 and self.power_status:  # Source type and ON
            return self.get_current_power()
        return 0


class Appliance_Summary:
    def __init__(self, name="All", ID=0):
        self.name = name
        self.ID = ID
        self.type = -1  # Special type for "All"
        self.power_status = True  # Always "active"
        
        # Summary properties
        self.total_power_consumption = 0    # Total power consumed by all loads
        self.total_power_generation = 0     # Total power generated by all sources
        self.total_energy_consumption = 0   # Total energy consumed by all appliances
        self.total_energy_generated = 0     # Total energy generated by all sources
        
        # Power history for summary
        self.power = [0] * 300  # Array tracking net power (generation - consumption)
        
        # Standard properties (for compatibility)
        self.voltage_rating = 240  # System voltage
        self.power_rating = 0
        self.fault = False
        self.time_operated = 0
        
    def update_power_value(self, consumption, generation):
        net_power = consumption - generation
        
        # Shift all values left by one position
        self.power[:-1] = self.power[1:]
        # Add new value at the end
        self.power[-1] = net_power
        
        # Update summary values
        self.total_power_consumption = consumption
        self.total_power_generation = generation
        
    def get_current_power(self):
        return self.power[-1]

    def get_power_history(self):
        return self.power.copy()
        

    def update_from_appliances(self, appliances_dict):
        """Update aggregate values from all individual appliances"""
        # Reset values
        total_consumption = 0
        total_generation = 0
        self.total_energy_consumption = 0
        self.total_energy_generated = 0
        total_time = 0
        active_count = 0
        
        # Aggregate data from all appliances
        for name, appliance in appliances_dict.items():
            if name == "All" or appliance is None:
                continue
                
            # Power consumption (loads)
            if appliance.type == 0:  # Load
                total_consumption += appliance.get_power_consumption()
                self.total_energy_consumption += appliance.energy_used
            
            # Power generation (sources) 
            elif appliance.type == 1:  # Source
                total_generation += appliance.get_power_generation()
                self.total_energy_generated += appliance.energy_used
            
            # Storage contributes to both consumption and generation based on mode
            elif appliance.type == 2:  # Storage
                self.total_energy_consumption += appliance.energy_used
            
            # Aggregate time operated
            if appliance.power_status:
                total_time += appliance.time_operated
                active_count += 1
        
        # Update current consumption and generation
        self.total_power_consumption = total_consumption
        self.total_power_generation = total_generation
        self.time_operated = total_time // active_count if active_count > 0 else 0
        
        # Update net power (generation - consumption)
        self.power_rating = total_generation - total_consumption

    # MISSING METHODS - ADD THESE FOR COMPATIBILITY:
    def properties(self):
        """Return summary properties for 'All' appliances"""
        return {
            'name': self.name,
            'type': self.type,
            'total_power_consumption': self.total_power_consumption,
            'total_power_generation': self.total_power_generation,
            'total_energy_consumption': self.total_energy_consumption,
            'total_energy_generated': self.total_energy_generated,
            'net_power': self.power_rating,
            'system_voltage': self.voltage_rating,
            'fault': self.fault
        }

    def get_status_text(self):
        return "ON" if self.power_status else "OFF"
    
    def get_status_color(self):
        return 'green' if self.power_status else 'red'

    def toggle_power(self):
        if self.power_status:
            self.power_status = False
        else:
            self.power_status = True

    def get_power_consumption(self):
        return self.total_power_consumption

    def get_power_generation(self):
        return self.total_power_generation


class Upper_GUI:
    def __init__ (self,root, right_gui, appliances):
        self.root = root
        self.right_gui = right_gui
        self.appliances = appliances

        self.frame_appliance = LabelFrame(root, text="Appliance", 
                                padx=5, pady=5, bg="white")
        self.frame_power = LabelFrame(root, text="Power", 
                                padx=5, pady=5, bg="white")
        self.frame_options = LabelFrame(root, text="Options", 
                                padx=5, pady=5, bg="white")

        self.OptionMenu()
        self.btn_power = Button(self.frame_power, text="OFF", bg='red', width=10, command=self.command_switch_power)
        
        # Create two separate buttons for options
        self.btn_logs = Button(self.frame_options, text="Logs", width=10, command=self.command_logs, state='disabled')
        self.btn_settings = Button(self.frame_options, text="Settings", width=10, command=self.command_settings)

        self.update_power_button()
        self.publish()

    def OptionMenu(self): #creates the dropdown menu
        appliance_names = list(self.appliances.keys())
        self.option_clicked = StringVar(self.root)
        self.option_clicked.set(appliance_names[1])  # Set to first appliance by default
        self.option_clicked.trace("w", self.on_appliance_change)
        self.dropdown = OptionMenu(self.frame_appliance, self.option_clicked, *appliance_names)
        self.dropdown.config(width=20)

    def on_appliance_change(self, *args): #calls when dropdown changes
        # Store current view state before switching
        current_view_is_settings = (hasattr(self, 'right_gui') and 
                                hasattr(self.right_gui, 'current_frame') and 
                                hasattr(self.right_gui, 'settings_frame') and
                                self.right_gui.current_frame == getattr(self.right_gui, 'settings_frame', None))
        
        current_view_is_logs = (hasattr(self, 'right_gui') and 
                            hasattr(self.right_gui, 'current_frame') and 
                            hasattr(self.right_gui, 'log_frame') and
                            self.right_gui.current_frame == getattr(self.right_gui, 'log_frame', None))
        
        # Update "All" appliances aggregate data if it exists
        if "All" in self.appliances and isinstance(self.appliances["All"], Appliance_Summary):
            self.appliances["All"].update_from_appliances(self.appliances)
        
        # Get the new appliance
        new_appliance = self.get_current_appliance()
        
        self.update_power_button()
        
        # Handle view switching logic based on appliance type and current view
        if isinstance(new_appliance, Appliance_Summary): #switch to 'All'
            self.right_gui.createLogs(self.root)
            self.btn_logs.config(state='disabled')
            self.btn_settings.config(state='disabled')  # Settings not available for "All"
        else:
            # Switching to individual appliance - maintain previous view if possible
            if current_view_is_settings:
                # Was in settings view, maintain it
                self.right_gui.createSettings(self.root)
                self.btn_settings.config(state='disabled')
                self.btn_logs.config(state='normal')
            elif current_view_is_logs:
                # Was in logs view, maintain it
                self.right_gui.createLogs(self.root)
                self.btn_logs.config(state='disabled')
                self.btn_settings.config(state='normal')
            else:
                # Default to logs view if unclear
                self.right_gui.createLogs(self.root)
                self.btn_logs.config(state='disabled')
                self.btn_settings.config(state='normal')
    
        # Update left GUI properties and graph
        if hasattr(self, 'left_gui'):
            self.left_gui.update_appliance_display(new_appliance)
            self.left_gui.update_graph(new_appliance)

    def get_current_appliance(self): #get object of current appliance
        current_appliance_name = self.option_clicked.get()
        return self.appliances.get(current_appliance_name)
    
    def update_power_button(self): #updates based on current selection
        current_appliance = self.get_current_appliance()
        if current_appliance is None:
            # No appliance selected
            self.btn_power.config(text="", bg='gray', state='disabled')
            self.btn_settings.config(state='disabled')
            self.btn_logs.config(state='disabled')
            self.right_gui.createLogs(self.root)  # Reset logs frame
        elif isinstance(current_appliance, Appliance_Summary):
            self.btn_power.config(text="--", bg='gray', state='disabled')
        else:
            # Normal handling for individual appliances
            self.btn_power.config(text=current_appliance.get_status_text(),
                                bg=current_appliance.get_status_color(), state='normal')
        
    def publish(self):
        self.frame_appliance.grid(row=0, column=0, rowspan=3, columnspan=3, padx=5, pady=5)    
        self.frame_power.grid(row=0, column=3, rowspan=3, columnspan=3, padx=5, pady=5)
        self.root.grid_columnconfigure(6, weight=1) 
        self.frame_options.grid(row=0, column=6, rowspan=3, padx=5, pady=5, sticky='e') 
        self.dropdown.grid(row=2, column=0, padx=5, pady=5)
        self.btn_power.grid(row=2, column=3, padx=5, pady=7)
        
        # Grid the two option buttons
        self.btn_logs.grid(row=1, column=5, padx=5, pady=3, sticky='e') 
        self.btn_settings.grid(row=1, column=6, padx=5, pady=3, sticky='e') 

    def command_switch_power(self):
        current_appliance = self.get_current_appliance()
        current_name = self.option_clicked.get()
        # Toggle individual appliance
        if current_appliance.power_status:
            current_appliance.toggle_power()
            self.right_gui.log_events(f"{current_name} turned OFF")
        else:
            current_appliance.toggle_power()
            self.right_gui.log_events(f"{current_name} turned ON")
        
        # Update "All" aggregate data
        if "All" in self.appliances and isinstance(self.appliances["All"], Appliance_Summary):
            self.appliances["All"].update_from_appliances(self.appliances)

        self.update_power_button()
        # Update the left GUI with the current appliance's properties
        if hasattr(self, 'left_gui'):
            self.left_gui.update_appliance_display(current_appliance)

    def command_logs(self):
        self.right_gui.createLogs(self.root)
        self.btn_logs.config(state='disabled')  # Disable after clicking
        self.btn_settings.config(state='normal')  # Enable settings button

    def command_settings(self):
        self.right_gui.createSettings(self.root)
        self.btn_settings.config(state='disabled')  # Disable after clicking
        self.btn_logs.config(state='normal')  # Enable logs button


class Left_GUI:
    def __init__ (self, root, data):
        self.root = root
        self.data = data 
        self.current_appliance = None  # Track currently displayed appliance

        self.addFrame()
        
    def addFrame(self):
        self.frame_graph = LabelFrame(self.root, text="Graphic Display", 
                            padx=5, pady=5, bg="white")
        self.frame_graph.grid(row=4, column=0, rowspan=6, columnspan=6, padx=5, pady=3, sticky='nsew')

        self.frame_stats = LabelFrame(self.root, text="Properties",
                            padx=5, pady=0, bg="white")
        self.frame_stats.grid(row=6, column=0, rowspan=5, columnspan=6, padx=5, pady=3, sticky='nsew')

        # Configure row and column weights for proper alignment
        self.frame_stats.grid_rowconfigure(0, weight=1)
        self.frame_stats.grid_columnconfigure(0, weight=1)
        self.frame_stats.grid_columnconfigure(3, weight=1)

        # Create labels that will be dynamically updated
        self.label_stats1 = Label(self.frame_stats, text="Power:", bg="white")
        self.label_stats2 = Label(self.frame_stats, text="Voltage:", bg="white")
        self.label_stats3 = Label(self.frame_stats, text="Current:", bg="white")
        self.label_stats4 = Label(self.frame_stats, text="Energy used:", bg="white")
        self.label_stats5 = Label(self.frame_stats, text="Time operated:", bg="white")
        self.label_stats6 = Label(self.frame_stats, text="Fault:", bg="white")

        # Create value labels
        self.label_stats1_value = Label(self.frame_stats, text="0 W", bg="white")
        self.label_stats2_value = Label(self.frame_stats, text="0 V", bg="white")
        self.label_stats3_value = Label(self.frame_stats, text="0 A", bg="white")
        self.label_stats4_value = Label(self.frame_stats, text="0 kWh", bg="white")
        self.label_stats5_value = Label(self.frame_stats, text="0 min", bg="white")
        self.label_stats6_value = Label(self.frame_stats, text="No Fault", bg="white") 

        # Initial graph setup
        self.setup_graph()
        
        # Initial grid layout (will be updated dynamically)
        self.setup_individual_appliance_layout()

    def setup_graph(self):
        """Setup the initial graph"""
        self.fig = plt.Figure(figsize=(5,3), dpi=80)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('Time (HH:MM)')
        self.ax.set_ylabel('Power (W)')
        self.ax.grid(True)
        
        # CHANGED: Initialize with fixed time axis (5-minute window)
        current_time = datetime.now()
        start_time = current_time - timedelta(seconds=299)
        end_time = current_time
    
        # Create fixed time axis - this won't change
        self.time_axis = []
        for i in range(300):
            timestamp = start_time + timedelta(seconds=i)
            self.time_axis.append(timestamp)
    
        self.line, = self.ax.plot(self.time_axis, [0]*300, label='Power')
        
        # CHANGED: Set fixed x-axis limits that don't change
        self.ax.set_xlim(start_time, end_time)
        
        # Configure time formatting
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
        plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Initialize data counter
        self.data_count = 0
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_graph)
        self.canvas.get_tk_widget().grid(column=0, row=2, columnspan=3, sticky=NSEW)

    def update_graph(self, appliance):
        """Update graph with appliance's power history"""
        if appliance is None:
            return
            
        self.current_appliance = appliance
        power_history = appliance.get_power_history()
        
        # fixed time axis, only update power data
        self.line.set_ydata(power_history)
        
        # Update graph title and labels based on appliance type
        if isinstance(appliance, Appliance_Summary):
            self.ax.set_ylabel('Net Power (W)')
        else:
            self.ax.set_ylabel('Power (W)')
        
        # Auto-scale y-axis only
        self.ax.relim()
        self.ax.autoscale_view(scalex=False, scaley=True)
        
        # Adjust layout to prevent label cutoff
        self.fig.tight_layout()
        
        # Redraw the canvas
        self.canvas.draw()

    def refresh_current_graph(self):
        """Refresh the graph for the currently displayed appliance"""
        if self.current_appliance is not None:
            # CHANGED: Update the fixed time axis to current time window
            current_time = datetime.now()
            start_time = current_time - timedelta(seconds=299)
            end_time = current_time
            
            # Update the time axis to current 5-minute window
            for i in range(300):
                self.time_axis[i] = start_time + timedelta(seconds=i)
            
            # Update x-axis limits to current window
            self.ax.set_xlim(start_time, end_time)
            
            # Update the line's x-data with new time axis
            self.line.set_xdata(self.time_axis)
            
            # Increment data counter
            self.data_count += 1
            self.update_graph(self.current_appliance)

    def setup_individual_appliance_layout(self):
        # Clear all widgets first
        for widget in self.frame_stats.winfo_children():
            widget.grid_forget()
        
        # Standard layout for individual appliances
        self.label_stats1.config(text="Power:")
        self.label_stats2.config(text="Voltage:")
        self.label_stats3.config(text="Current:")
        self.label_stats4.config(text="Energy used:")
        self.label_stats5.config(text="Time operated:")
        self.label_stats6.config(text="Fault:")

        self.label_stats1.grid(row=0, column=0, padx=5, pady=3, sticky='w')
        self.label_stats2.grid(row=1, column=0, padx=5, pady=3, sticky='w')
        self.label_stats3.grid(row=2, column=0, padx=5, pady=3, sticky='w')
        self.label_stats4.grid(row=0, column=3, padx=5, pady=3, sticky="w") 
        self.label_stats5.grid(row=1, column=3, padx=5, pady=3, sticky="w")
        self.label_stats6.grid(row=2, column=3, padx=5, pady=3, sticky="w") 

        self.label_stats1_value.grid(row=0, column=1, padx=5, pady=3, sticky='e')
        self.label_stats2_value.grid(row=1, column=1, padx=5, pady=3, sticky='e')
        self.label_stats3_value.grid(row=2, column=1, padx=5, pady=3, sticky='e')
        self.label_stats4_value.grid(row=0, column=4, padx=5, pady=3, sticky="e") 
        self.label_stats5_value.grid(row=1, column=4, padx=5, pady=3, sticky="e")
        self.label_stats6_value.grid(row=2, column=4, padx=5, pady=3, sticky="e")

    def setup_summary_layout(self):
        # Clear all widgets first
        for widget in self.frame_stats.winfo_children():
            widget.grid_forget()
        
        # Summary layout - only 4 parameters
        self.label_stats1.config(text="Total Power Use:")
        self.label_stats2.config(text="Total Power Generation:")
        self.label_stats3.config(text="Total Energy Use:")
        self.label_stats4.config(text="Total Energy Generated:")

        # Grid them in a 2x2 layout
        self.label_stats1.grid(row=0, column=0, padx=5, pady=3, sticky='w')
        self.label_stats2.grid(row=0, column=3, padx=5, pady=3, sticky='w')
        self.label_stats3.grid(row=1, column=0, padx=5, pady=3, sticky="w") 
        self.label_stats4.grid(row=1, column=3, padx=5, pady=3, sticky='w')

        self.label_stats1_value.grid(row=0, column=1, padx=5, pady=3, sticky='e')
        self.label_stats2_value.grid(row=0, column=4, padx=5, pady=3, sticky='e')
        self.label_stats3_value.grid(row=1, column=1, padx=5, pady=3, sticky="e") 
        self.label_stats4_value.grid(row=1, column=4, padx=5, pady=3, sticky="e")

    def update_appliance_display(self, appliance):        
        if isinstance(appliance, Appliance_Summary):
            # Show summary layout and data for "All"
            self.setup_summary_layout()
            self.label_stats1_value.config(text=f"{appliance.total_power_consumption:.1f} W")
            self.label_stats2_value.config(text=f"{appliance.total_power_generation:.1f} W")
            self.label_stats3_value.config(text=f"{appliance.total_energy_consumption:.3f} kWh")
            self.label_stats4_value.config(text=f"{appliance.total_energy_generated:.3f} kWh")
        else:
            # Show individual appliance layout and data
            self.setup_individual_appliance_layout()
            current_power = appliance.get_current_power() if appliance.power_status else 0
            voltage = appliance.voltage_rating if appliance.voltage_rating > 0 else 300  # Default voltage
            current = current_power / voltage if voltage > 0 else 0
            
            self.label_stats1_value.config(text=f"{current_power:.1f} W")
            self.label_stats2_value.config(text=f"{voltage} V")
            self.label_stats3_value.config(text=f"{current:.2f} A")
            self.label_stats4_value.config(text=f"{appliance.energy_used:.3f} kWh")
            self.label_stats5_value.config(text=f"{appliance.time_operated} sec")
            self.label_stats6_value.config(text="Fault" if appliance.fault else "No Fault")


class DataUpdateManager:
    def __init__(self, appliances, value_generator, left_gui, right_gui):
        self.appliances = appliances
        self.value_generator = value_generator
        self.left_gui = left_gui
        self.right_gui = right_gui
        self.running = False
        self.update_thread = None
        
    def start_updates(self):
        """Start the data update thread"""
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
    def stop_updates(self):
        """Stop the data update thread"""
        self.running = False
        
    def _update_loop(self):
        """Main update loop that runs every second"""
        while self.running:
            try:
                # Update individual appliances
                for name, appliance in self.appliances.items():
                    if name == "All" or appliance is None:
                        continue
                        
                    # Generate new power value
                    new_power = self.value_generator.generate_value(name, appliance.power_status)
                    appliance.update_power_value(new_power)
                
                # Update summary appliance
                if "All" in self.appliances:
                    summary = self.appliances["All"]
                    consumption, generation = self.value_generator.generate_summary_values(self.appliances)
                    summary.update_power_value(consumption, generation)
                    summary.update_from_appliances(self.appliances)
                
                # Update GUI in main thread
                self.left_gui.root.after(0, self._update_gui)
                
                # Wait for 1 second
                time.sleep(1)
                
            except Exception as e:
                print(f"Error in update loop: {e}")
                
    def _update_gui(self):
        """Update GUI elements (called in main thread)"""
        try:
            # Refresh the graph for currently displayed appliance
            self.left_gui.refresh_current_graph()
            
            # Update properties display for current appliance
            if hasattr(self.left_gui, 'current_appliance') and self.left_gui.current_appliance:
                self.left_gui.update_appliance_display(self.left_gui.current_appliance)
                
        except Exception as e:
            print(f"Error updating GUI: {e}")


class Right_GUI:
    def __init__(self, root, upper_gui=None):
        self.root = root
        self.upper_gui = upper_gui
        self.current_frame = None
        self.log_data = [] # Store log data
        self.createLogs(root)  # Initialize with logs frame

    def createLogs(self, root):
        if self.current_frame:
            self.current_frame.destroy()
        self.log_frame = LabelFrame(root, text="Logs", 
                                    padx=5, pady=3, bg="white")
        self.log_frame.grid(row=4, column=6, rowspan=4, padx=5, pady=3, sticky='nsew')
        
        # Set as current frame
        self.current_frame = self.log_frame

        # Create the scrollbar
        self.scrollbar = Scrollbar(self.log_frame)
        self.scrollbar.grid(row=0, column=1, sticky='ns') 

        # Create the textbox
        self.log_textbox = Text(self.log_frame, bg='white',
                                wrap="word", state="disabled", yscrollcommand=self.scrollbar.set)
        self.log_textbox.grid(row=0, column=0, sticky="nsew")

        self.log_frame.grid_rowconfigure(0, weight=1)
        self.log_frame.grid_columnconfigure(0, weight=1)

        # Configure scrollbar to scroll the textbox
        self.scrollbar.config(command=self.log_textbox.yview)

        # Log initial event
        self.restore_logs()

    def createSettings(self, root):
        # Remove current frame
        if self.current_frame:
            self.current_frame.destroy()
            
        self.settings_frame = LabelFrame(root, text="Settings", 
                                    padx=5, pady=3, bg="white")
        self.settings_frame.grid(row=4, column=6, rowspan=5, padx=5, pady=3, sticky='nsew')
        
        # Set as current frame
        self.current_frame = self.settings_frame
        
        # Appliance Type Selection
        self.setting1 = Label(self.settings_frame, text="Appliance Type:", bg="white")
        self.setting1.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        
        appliance_types = ["Load", "Source", "Storage"]
        self.selected_type = StringVar(self.settings_frame)
        
        # Get current appliance and set appropriate type
        current_appliance = None
        if self.upper_gui:
            current_appliance = self.upper_gui.get_current_appliance()
            if current_appliance is not None and not isinstance(current_appliance, Appliance_Summary):
                # Set type based on appliance's stored type
                if current_appliance.type == 0:
                    self.selected_type.set("Load")
                elif current_appliance.type == 1:
                    self.selected_type.set("Source")
                elif current_appliance.type == 2:
                    self.selected_type.set("Storage")
                else:
                    self.selected_type.set(appliance_types[0])  # Default
            else:
                self.selected_type.set(appliance_types[0])  # Default for "All"
        else:
            self.selected_type.set(appliance_types[0])  # Default
        
        self.selected_type.trace('w', self.on_type_change)  # Add trace to detect changes
        
        self.dropdown1 = OptionMenu(self.settings_frame, self.selected_type, *appliance_types)
        self.dropdown1.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        self.dropdown1.config(width=15)
        
        # Store current appliance for use in create_dynamic_settings
        self.current_appliance_for_settings = current_appliance
        
        # Create dynamic settings based on selected type
        self.create_dynamic_settings()

    def on_type_change(self, *args):
        # Update the current appliance reference when type changes
        if self.upper_gui:
            self.current_appliance_for_settings = self.upper_gui.get_current_appliance()
        self.create_dynamic_settings()

    def create_dynamic_settings(self):
        # Clear existing dynamic widgets if they exist
        if hasattr(self, 'dynamic_widgets'):
            for widget in self.dynamic_widgets:
                widget.destroy()
        
        self.dynamic_widgets = []
        self.setting_entries = {}  # Store entry widgets for later access
        
        selected_type = self.selected_type.get()
        current_appliance = getattr(self, 'current_appliance_for_settings', None)
        
        # Don't show settings for Appliance_Summary
        if isinstance(current_appliance, Appliance_Summary):
            label = Label(self.settings_frame, text="Settings not available for 'All' view", bg="white")
            label.grid(row=2, column=0, columnspan=2, padx=5, pady=20)
            self.dynamic_widgets.append(label)
            return
        
        if selected_type == "Load":
            # Load Settings with values from current appliance
            if current_appliance and current_appliance.type == 0:
                settings = [
                    ("Rated Power (W):", str(current_appliance.power_rating) if current_appliance.power_rating > 0 else ""),
                    ("Rated Voltage (V):", str(current_appliance.voltage_rating) if current_appliance.voltage_rating > 0 else ""),
                    ("Max Current (A):", str(current_appliance.max_current) if current_appliance.max_current > 0 else ""),
                    ("Overvoltage Threshold (V):", str(current_appliance.overvoltage_threshold) if current_appliance.overvoltage_threshold > 0 else ""),
                    ("Undervoltage Threshold (V):", str(current_appliance.undervoltage_threshold) if current_appliance.undervoltage_threshold > 0 else ""),
                    ("Differential Threshold (A):", str(current_appliance.differential_threshold) if current_appliance.differential_threshold > 0 else ""),
                ]
            else:
                settings = [
                    ("Rated Power (W):", ""),
                    ("Rated Voltage (V):", ""),
                    ("Max Current (A):", ""),
                    ("Overvoltage Threshold (V):", ""),
                    ("Undervoltage Threshold (V):", ""),
                    ("Differential Threshold (A):", ""),
                ]
        
        elif selected_type == "Source":
            # Source Settings with values from current appliance
            if current_appliance and current_appliance.type == 1:
                settings = [
                    ("Max Output Power (W):", str(current_appliance.max_output_power) if current_appliance.max_output_power > 0 else ""),
                    ("Output Voltage (V):", str(current_appliance.voltage_rating) if current_appliance.voltage_rating > 0 else ""),
                    ("Max Output Current (A):", str(current_appliance.max_output_current) if current_appliance.max_output_current > 0 else ""),
                    ("Undervoltage Threshold (V):", str(current_appliance.undervoltage_threshold) if current_appliance.undervoltage_threshold > 0 else ""),
                ]
            else:
                settings = [
                    ("Max Output Power (W):", ""),
                    ("Output Voltage (V):", ""),
                    ("Max Output Current (A):", ""),
                    ("Undervoltage Threshold (V):", ""),
                ]
        
        else:  # Storage
            # Storage Settings with values from current appliance
            if current_appliance and current_appliance.type == 2:
                settings = [
                    ("Capacity (Wh):", str(current_appliance.capacity) if current_appliance.capacity > 0 else ""),
                    ("Rated Voltage (V):", str(current_appliance.voltage_rating) if current_appliance.voltage_rating > 0 else ""),
                    ("Max Charge Current (A):", str(current_appliance.max_charge_current) if current_appliance.max_charge_current > 0 else ""),
                    ("Max Discharge Current (A):", str(current_appliance.max_discharge_current) if current_appliance.max_discharge_current > 0 else ""),
                ]
            else:
                settings = [
                    ("Capacity (Wh):", ""),
                    ("Rated Voltage (V):", ""),
                    ("Max Charge Current (A):", ""),
                    ("Max Discharge Current (A):", ""),
                ]
        
        # Create labels and entries for each setting
        for i, (label_text, default_value) in enumerate(settings):
            row = i + 2  # Start from row 2 (after appliance type)
            
            # Create label
            label = Label(self.settings_frame, text=label_text, bg="white")
            label.grid(row=row, column=0, padx=5, pady=3, sticky='w')
            self.dynamic_widgets.append(label)
            
            # Create entry
            entry = Entry(self.settings_frame)
            entry.insert(0, default_value)  # Set saved value or empty string
            self.setting_entries[f'setting_{i}'] = entry
            
            entry.grid(row=row, column=1, padx=5, pady=3, sticky='ew')
            self.dynamic_widgets.append(entry)
        
        # Add Save button at the bottom
        save_row = len(settings) + 2
        self.btn_save_data = Button(self.settings_frame, text="Save Settings", 
                                width=15, command=self.save_settings,
                                bg='lightblue', cursor='hand2')
        self.btn_save_data.grid(row=save_row, column=0, columnspan=2, padx=5, pady=10)
        self.dynamic_widgets.append(self.btn_save_data)
        
        # Configure grid weights
        self.settings_frame.grid_columnconfigure(1, weight=1)

    def save_settings(self):
        selected_type = self.selected_type.get()
        settings_data = {}
        
        # Get all entry values
        for key, widget in self.setting_entries.items():
            if isinstance(widget, Entry):
                settings_data[key] = widget.get()
            elif isinstance(widget, StringVar):
                settings_data[key] = widget.get()
        
        # Get the current appliance from Upper_GUI
        if self.upper_gui:
            current_appliance = self.upper_gui.get_current_appliance()
            if current_appliance is not None and not isinstance(current_appliance, Appliance_Summary):
                self.update_appliance_properties(current_appliance, selected_type, settings_data)
                
                # Log the saved settings with appliance name
                self.log_events(f"Settings saved for {current_appliance.name} ({selected_type})")
                # Show confirmation with appliance name
                msgbox.showinfo("Settings Saved", 
                              f"Settings for '{current_appliance.name}' have been saved successfully!")
            else:
                msgbox.showwarning("Cannot Save", "Please select a specific appliance (not 'All') to save settings.")
        else:
            # Fallback logging if no upper_gui reference
            self.log_events(f"Settings saved for {selected_type}")
            for key, value in settings_data.items():
                if value:
                    self.log_events(f"  {key}: {value}")

    def update_appliance_properties(self, appliance, appliance_type, settings_data):
        # Set appliance type
        if appliance_type == "Load":
            appliance.type = 0
        elif appliance_type == "Source":
            appliance.type = 1
        elif appliance_type == "Storage":
            appliance.type = 2
        
        # Update properties based on appliance type and settings
        if appliance_type == "Load":
            # Load Settings
            for key, value in settings_data.items():
                if not value:  # Skip empty values
                    continue
                try:
                    if 'setting_0' in key:  # Rated Power (W)
                        appliance.power_rating = float(value)
                    elif 'setting_1' in key:  # Rated Voltage (V)
                        appliance.voltage_rating = float(value)
                    elif 'setting_2' in key:  # Max Current (A)
                        appliance.max_current = float(value)
                    elif 'setting_3' in key:  # Overvoltage Threshold (V)
                        appliance.overvoltage_threshold = float(value)
                    elif 'setting_4' in key:  # Undervoltage Threshold (V)
                        appliance.undervoltage_threshold = float(value)
                    elif 'setting_5' in key:  # Differential Threshold (A)
                        appliance.differential_threshold = float(value)
                except ValueError:
                    self.log_events(f"Warning: Invalid value '{value}' for {key}")
        
        elif appliance_type == "Source":
            # Source Settings
            for key, value in settings_data.items():
                if not value:  # Skip empty values
                    continue
                    
                try:
                    if 'setting_0' in key:  # Max Output Power (W)
                        appliance.max_output_power = float(value)
                    elif 'setting_1' in key:  # Output Voltage (V)
                        appliance.voltage_rating = float(value)
                    elif 'setting_2' in key:  # Max Output Current (A)
                        appliance.max_output_current = float(value)
                    elif 'setting_3' in key:  # Undervoltage Threshold (V)
                        appliance.undervoltage_threshold = float(value)
                except ValueError:
                    self.log_events(f"Warning: Invalid value '{value}' for {key}")
        
        elif appliance_type == "Storage":
            # Storage Settings
            for key, value in settings_data.items():
                if not value:  # Skip empty values
                    continue
                try:
                    if 'setting_0' in key:  # Capacity (Wh)
                        appliance.capacity = float(value)
                    elif 'setting_1' in key:  # Rated Voltage (V)
                        appliance.voltage_rating = float(value)
                    elif 'setting_2' in key:  # Max Charge Current (A)
                        appliance.max_charge_current = float(value)
                    elif 'setting_3' in key:  # Max Discharge Current (A)
                        appliance.max_discharge_current = float(value)
                except ValueError:
                    self.log_events(f"Warning: Invalid value '{value}' for {key}")
        
        # Log successful update
        self.log_events(f"Appliance '{appliance.name}' properties updated successfully")
        

    def log_events(self, message):
        timestamp = datetime.now().strftime("%d/%m %H:%M:%S")
        entry = f"[{timestamp}] {message}\n"
        self.log_data.append(entry)  # Store log data
        if hasattr(self, 'log_textbox') and self.log_textbox.winfo_exists():
            self.log_textbox.configure(state="normal")
            self.log_textbox.insert("end", entry)
            self.log_textbox.configure(state="disabled")
            self.log_textbox.see("end")

    def restore_logs(self):
        if hasattr(self, 'log_textbox') and self.log_data:
            self.log_textbox.configure(state="normal")
            self.log_textbox.delete("1.0", "end")
            for entry in self.log_data:
                self.log_textbox.insert("end", entry)
            self.log_textbox.configure(state="disabled")
            self.log_textbox.see("end")


if __name__ == "__main__":
    # Create individual appliances
    washing_machine = Appliance("Washing Machine", 1)
    washing_machine.power_rating = 500
    washing_machine.voltage_rating = 250
    washing_machine.type = 0  # Load
    
    air_conditioner = Appliance("Air Conditioner", 2)
    air_conditioner.power_rating = 1200
    air_conditioner.voltage_rating = 200
    air_conditioner.type = 0  # Load
    
    heater = Appliance("Heater", 3)
    heater.power_rating = 800
    heater.voltage_rating = 150
    heater.type = 0  # Load
    
    # Create summary appliance
    appliance_summary = Appliance_Summary("All", 0)
    
    appliances = {
        "All": appliance_summary,
        "Washing Machine": washing_machine,
        "Air Conditioner": air_conditioner,
        "Heater": heater
    }
    
    # Create random value generator and set parameters
    value_generator = RandomValueGenerator()
    value_generator.set_appliance_parameters("Washing Machine", 500, 15)  # ±15% variation
    value_generator.set_appliance_parameters("Air Conditioner", 1200, 20)  # ±20% variation
    value_generator.set_appliance_parameters("Heater", 800, 10)  # ±10% variation
    
    # Initialize summary with current appliance data
    appliance_summary.update_from_appliances(appliances)
    
    # Initialising GUI components
    root_gui = RootGUI()
    upper_gui = Upper_GUI(root_gui.root, None, appliances) 
    right_gui = Right_GUI(root_gui.root, upper_gui)
    upper_gui.right_gui = right_gui
    left_gui = Left_GUI(root_gui.root, 0)
    upper_gui.left_gui = left_gui

    # Create and start data update manager
    data_manager = DataUpdateManager(appliances, value_generator, left_gui, right_gui)
    data_manager.start_updates()

    # Initialize with first appliance selected
    initial_appliance = upper_gui.get_current_appliance()
    left_gui.update_appliance_display(initial_appliance)
    left_gui.update_graph(initial_appliance)

    #Initialising GUI notification
    right_gui.log_events("GUI initialized")

    root_gui.root.mainloop()
    
    # Stop data updates when GUI closes
    data_manager.stop_updates()