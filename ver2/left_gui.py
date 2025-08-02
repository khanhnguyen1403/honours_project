from tkinter import *
from tkinter import messagebox as msgbox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from appliance import Appliance_Summary

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
        self.fig = plt.Figure(figsize=(5,3.5), dpi=80)
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
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        self.ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
        plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=0, ha='right')
        
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
        
        # CHANGED: Set y-axis limits from 0 to max value
        max_value = max(power_history) if power_history else 0
        min_value = min(power_history) if power_history else 0
        
        # For summary appliances, handle negative values (net power can be negative)
        if isinstance(appliance, Appliance_Summary):
            if min_value < 0:
                # If there are negative values, show from min to max
                y_min = min_value - abs(min_value) * 0.1  # Add 10% padding below
                y_max = max_value + abs(max_value) * 0.1 if max_value > 0 else 10  # Add 10% padding above
            else:
                # All positive, show from 0 to max
                y_min = 0
                y_max = max_value + max_value * 0.1 if max_value > 0 else 10
        else:
            # For individual appliances, always start from 0
            y_min = 0
            y_max = max_value + max_value * 0.1 if max_value > 0 else 10  # Add 10% padding above max
        
        self.ax.set_ylim(y_min, y_max)
        
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

