from tkinter import *
from tkinter import messagebox as msgbox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from appliance import Appliance_Summary


class Left_GUI:
    """
    Left GUI class handles the graphical display and properties panel of appliances.
    Contains a real-time power consumption graph and detailed appliance statistics.
    """
    def __init__(self, root, data):
        """
        Initialize the Left GUI component.
        """
        self.root = root
        self.data = data 
        self.current_appliance = None  # Track currently displayed appliance
        self.appliances = {}  # Reference to all appliances for summary view
        
        # Initialize GUI components
        self.addFrame()

    def set_appliances(self, appliances):
        """
        Set the appliances reference for multi-line graph display.
        """
        self.appliances = appliances
        
    def addFrame(self):
        """
        Create and configure the main frames for the left GUI.
        Sets up the graph display frame and properties frame with proper grid layout.
        """
        # Create graph display frame
        self.frame_graph = LabelFrame(self.root, text="Graphic Display", padx=5, pady=5, bg="white")
        self.frame_graph.grid(row=4, column=0, rowspan=6, columnspan=6, padx=5, pady=3, sticky='nsew')

        # Create properties/statistics frame
        self.frame_stats = LabelFrame(self.root, text="Properties",padx=5, pady=0, bg="white")
        self.frame_stats.grid(row=6, column=0, rowspan=5, columnspan=6, padx=5, pady=3, sticky='nsew')

        # Configure grid weights for proper resizing behavior
        self.frame_stats.grid_rowconfigure(0, weight=1)
        self.frame_stats.grid_columnconfigure(0, weight=1)
        self.frame_stats.grid_columnconfigure(3, weight=1)

        # Initialize all label widgets for appliance properties
        self._create_property_labels()
        self._create_value_labels()

        # Setup initial components
        self.setup_graph()
        self.setup_individual_appliance_layout()

    def _create_property_labels(self):
        """
        Create labels for appliance property names.
        These labels will be dynamically repositioned based on appliance type.
        """
        self.label_stats1 = Label(self.frame_stats, text="Power:", bg="white")
        self.label_stats2 = Label(self.frame_stats, text="Duty Cycle:", bg="white")
        self.label_stats3 = Label(self.frame_stats, text="Frequency:", bg="white")
        self.label_stats4 = Label(self.frame_stats, text="Energy used:", bg="white")
        self.label_stats5 = Label(self.frame_stats, text="Time operated:", bg="white")
        self.label_stats6 = Label(self.frame_stats, text="Fault:", bg="white")

    def _create_value_labels(self):
        """
        Create labels for displaying appliance property values.
        These will be updated with real-time data from the selected appliance.
        """
        self.label_stats1_value = Label(self.frame_stats, text="0 W", bg="white")
        self.label_stats2_value = Label(self.frame_stats, text="0 %", bg="white")
        self.label_stats3_value = Label(self.frame_stats, text="0 kHz", bg="white")
        self.label_stats4_value = Label(self.frame_stats, text="0 Wh", bg="white")
        self.label_stats5_value = Label(self.frame_stats, text="0 min", bg="white")
        self.label_stats6_value = Label(self.frame_stats, text="No Fault", bg="white")

    def setup_graph(self):
        """
        Initialize the matplotlib graph for displaying real-time power consumption.
        Creates a fixed 5-minute time window that scrolls with current time.
        """
        # Create matplotlib figure and axis
        self.fig = plt.Figure(figsize=(5, 3.5), dpi=80)
        self.ax = self.fig.add_subplot(111)
        
        # Configure graph appearance
        self.ax.set_xlabel('Time (HH:MM)')
        self.ax.set_ylabel('Power (W)')
        self.ax.grid(True)
        
        # Initialize fixed 5-minute time window
        current_time = datetime.now()
        start_time = current_time - timedelta(seconds=299)  # 299 seconds = ~5 minutes
        end_time = current_time
    
        # Create time axis with 1-second intervals (300 data points)
        self.time_axis = []
        for i in range(300):
            timestamp = start_time + timedelta(seconds=i)
            self.time_axis.append(timestamp)
    
        # Initialize power data line with zeros
        self.line, = self.ax.plot(self.time_axis, [0] * 300)
        
        # Initialize storage for multiple lines (for summary view)
        self.appliance_lines = {}  # Store individual appliance lines
        self.appliance_colors = [
            '#1f77b4',  # Blue
            '#ff7f0e',  # Orange
            '#2ca02c',  # Green
            '#d62728',  # Red
            '#9467bd',  # Purple
            '#8c564b',  # Brown
            '#e377c2',  # Pink
            '#7f7f7f',  # Gray
            '#bcbd22',  # Olive
            '#17becf',  # Cyan
            '#ff1493',  # Deep Pink
            '#00ff7f',  # Spring Green
            '#ffd700',  # Gold
            '#4169e1',  # Royal Blue
            '#dc143c'   # Crimson
        ]
        
        # Set fixed x-axis limits for the time window
        self.ax.set_xlim(start_time, end_time)
        
        # Configure time formatting for better readability
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        self.ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
        plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=0, ha='right')
        
        # Initialize data counter for tracking updates
        self.data_count = 0
        
        # Embed matplotlib canvas in tkinter frame
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_graph)
        self.canvas.get_tk_widget().grid(
            column=0, row=2, columnspan=3, sticky=NSEW
        )

    def update_graph(self, appliance):
        """
        Update the graph display with power data from the selected appliance.
        """
        if appliance is None:
            return
            
        # Store reference to current appliance for refresh operations
        self.current_appliance = appliance
        
        # Check if this is a summary view
        if isinstance(appliance, Appliance_Summary):
            self._update_summary_graph(appliance)
        else:
            self._update_individual_graph(appliance)
        
        # Optimize layout to prevent label cutoff
        self.fig.tight_layout()
        
        # Refresh the display
        self.canvas.draw()

    def _update_individual_graph(self, appliance):
        """
        Update graph for individual appliance.
        """
        # Clear any existing appliance lines from summary view
        self._clear_appliance_lines()
        
        # Show the main line and hide legend
        self.line.set_visible(True)
        self.ax.legend().set_visible(False) if self.ax.get_legend() else None
        
        # Get the appliance's power history data
        power_history = appliance.get_power_history()
        
        # Update only the power values, x-axis remains fixed
        self.line.set_ydata(power_history)
        
        # Configure graph labels
        self.ax.set_ylabel('Power (W)')
        
        # Calculate appropriate y-axis limits
        self._calculate_y_axis_limits(power_history, appliance)

    def _update_summary_graph(self, summary_appliance):
        """
        Update graph for summary view.
        """
        # Hide the main line for summary view
        self.line.set_visible(False)
        
        # Get all appliances
        appliances = self._get_all_appliances()
        
        # Clear existing appliance lines
        self._clear_appliance_lines()
        
        # Create lines for each individual appliance
        color_index = 0
        max_power = 0
        min_power = 0
        
        for name, appliance in appliances.items():
            if name == "All" or appliance is None:
                continue
                
            # Get power history for this appliance
            power_history = appliance.get_power_history()
            if not power_history:
                continue
            
            # Get color for this appliance
            color = self.appliance_colors[color_index % len(self.appliance_colors)]
            
            # Create line for this appliance
            line, = self.ax.plot(self.time_axis, power_history, 
                               label=f"{name}", color=color, linewidth=2)
            self.appliance_lines[name] = line
            
            # Track min/max for y-axis scaling
            max_power = max(max_power, max(power_history))
            min_power = min(min_power, min(power_history))
            
            color_index += 1
        
        # Add net power line (consumption - generation)
        net_power_history = summary_appliance.get_power_history()
        net_line, = self.ax.plot(self.time_axis, net_power_history, 
                               label="Net Power", color='black', linewidth=2)
        self.appliance_lines["Net Power"] = net_line
        
        # Include net power in min/max calculations
        if net_power_history:
            max_power = max(max_power, max(net_power_history))
            min_power = min(min_power, min(net_power_history))
        
        # Update y-axis limits based on all appliances with 10% padding
        if max_power > 0 or min_power < 0:
            # Calculate 10% padding based on the maximum absolute value
            y_range = max_power - min_power
            y_padding = max(y_range * 0.1, abs(max_power) * 0.1, abs(min_power) * 0.1) if y_range > 0 else max_power * 0.1
            
            # Set minimum to 0 unless there are negative values
            y_min = min_power - y_padding if min_power < 0 else 0
            y_max = max_power + y_padding
            
            self.ax.set_ylim(y_min, y_max)
        else:
            self.ax.set_ylim(0, 10)
        
        # Configure graph labels and legend 
        self.ax.set_ylabel('Power (W)')
        self.ax.legend(loc='upper left', fontsize=8)

    def _clear_appliance_lines(self):
        """
        Clear all individual appliance lines from the graph.
        """
        for line in self.appliance_lines.values():
            line.remove()
        self.appliance_lines.clear()
        
        # Clear legend if it exists
        if self.ax.get_legend():
            self.ax.get_legend().remove()

    def _get_all_appliances(self):
        """
        Get all appliances for multi-line graph display.
        """
        return self.appliances

    def _calculate_y_axis_limits(self, power_history, appliance):
        """
        Calculate and set appropriate y-axis limits for the graph.
        """
        if not power_history:
            self.ax.set_ylim(0, 10)
            return
            
        max_value = max(power_history)
        min_value = min(power_history)
        
        # Handle summary appliances (can have negative net power)
        if isinstance(appliance, Appliance_Summary):
            if min_value < 0:
                # Negative values present - show full range with padding
                y_min = min_value - abs(min_value) * 0.1
                y_max = max_value + abs(max_value) * 0.1 if max_value > 0 else 10
            else:
                # All positive - start from zero
                y_min = 0
                y_max = max_value + max_value * 0.1 if max_value > 0 else 10
        else:
            # Individual appliances - always start from zero
            y_min = 0
            y_max = max_value + max_value * 0.1 if max_value > 0 else 10
        
        self.ax.set_ylim(y_min, y_max)

    def refresh_current_graph(self):
        """
        Refresh the graph display with updated time window and current appliance data.
        This method is called periodically to update the scrolling time window.
        """
        if self.current_appliance is None:
            return
            
        # Update time window to current 5-minute window
        current_time = datetime.now()
        start_time = current_time - timedelta(seconds=299)
        end_time = current_time
        
        # Update the time axis to maintain a scrolling 5-minute window
        for i in range(300):
            self.time_axis[i] = start_time + timedelta(seconds=i)
        
        # Update x-axis limits to current time window
        self.ax.set_xlim(start_time, end_time)
        
        # Update the line's x-data with new time axis
        self.line.set_xdata(self.time_axis)
        
        # Update all appliance lines' x-data if in summary view
        for line in self.appliance_lines.values():
            line.set_xdata(self.time_axis)
        
        # Increment data counter for tracking
        self.data_count += 1
        
        # Refresh the graph with current appliance data
        self.update_graph(self.current_appliance)

    def setup_individual_appliance_layout(self):
        """
        Configure the properties panel layout for individual appliances.
        """
        # Clear any existing widgets
        self._clear_stats_frame()
        
        # Configure labels for individual appliance properties
        self.label_stats1.config(text="Power:")
        self.label_stats2.config(text="Duty Cycle:")
        self.label_stats3.config(text="Frequency:")
        self.label_stats4.config(text="Energy used:")
        self.label_stats5.config(text="Time operated:")
        self.label_stats6.config(text="Fault:")

        # Position property labels in left columns
        self.label_stats1.grid(row=0, column=0, padx=5, pady=3, sticky='w')
        self.label_stats2.grid(row=1, column=0, padx=5, pady=3, sticky='w')
        self.label_stats3.grid(row=2, column=0, padx=5, pady=3, sticky='w')
        self.label_stats4.grid(row=0, column=3, padx=5, pady=3, sticky="w") 
        self.label_stats5.grid(row=1, column=3, padx=5, pady=3, sticky="w")
        self.label_stats6.grid(row=2, column=3, padx=5, pady=3, sticky="w") 

        # Position value labels in right columns
        self.label_stats1_value.grid(row=0, column=1, padx=5, pady=3, sticky='e')
        self.label_stats2_value.grid(row=1, column=1, padx=5, pady=3, sticky='e')
        self.label_stats3_value.grid(row=2, column=1, padx=5, pady=3, sticky='e')
        self.label_stats4_value.grid(row=0, column=4, padx=5, pady=3, sticky="e") 
        self.label_stats5_value.grid(row=1, column=4, padx=5, pady=3, sticky="e")
        self.label_stats6_value.grid(row=2, column=4, padx=5, pady=3, sticky="e")

    def setup_summary_layout(self):
        """
        Configure the properties panel layout for summary/overview display.
        Shows system-wide totals: Power Use, Power Generation, Energy Use, Energy Generated.
        Uses a 2x2 grid layout for summary statistics.
        """
        # Clear any existing widgets
        self._clear_stats_frame()
        
        # Configure labels for summary statistics
        self.label_stats1.config(text="Total Power Use:")
        self.label_stats2.config(text="Total Power Generation:")
        self.label_stats3.config(text="Total Energy Use:")
        self.label_stats4.config(text="Total Energy Generated:")

        # Position summary labels in 2x2 grid
        self.label_stats1.grid(row=0, column=0, padx=5, pady=3, sticky='w')
        self.label_stats2.grid(row=0, column=3, padx=5, pady=3, sticky='w')
        self.label_stats3.grid(row=1, column=0, padx=5, pady=3, sticky="w") 
        self.label_stats4.grid(row=1, column=3, padx=5, pady=3, sticky='w')

        # Position corresponding value labels
        self.label_stats1_value.grid(row=0, column=1, padx=5, pady=3, sticky='e')
        self.label_stats2_value.grid(row=0, column=4, padx=5, pady=3, sticky='e')
        self.label_stats3_value.grid(row=1, column=1, padx=5, pady=3, sticky="e") 
        self.label_stats4_value.grid(row=1, column=4, padx=5, pady=3, sticky="e")

    def _clear_stats_frame(self):
        """
        Remove all widgets from the statistics frame.
        """
        for widget in self.frame_stats.winfo_children():
            widget.grid_forget()

    # Type-specific layout methods
    def _setup_load_layout(self):
        """
        Configure the properties panel layout for Load appliances.
        Power (W), Duty Cycle (%), Frequency (kHz), Energy Used (Wh), Time Operated (sec), Fault.
        """
        self._clear_stats_frame()
        
        # Configure labels for load appliance properties
        self.label_stats1.config(text="Power:")
        self.label_stats2.config(text="Duty Cycle:")
        self.label_stats3.config(text="Frequency:")
        self.label_stats4.config(text="Energy Used:")
        self.label_stats5.config(text="Time Operated:")
        self.label_stats6.config(text="Fault:")

        # Position property labels in left columns
        self.label_stats1.grid(row=0, column=0, padx=5, pady=3, sticky='w')
        self.label_stats2.grid(row=1, column=0, padx=5, pady=3, sticky='w')
        self.label_stats3.grid(row=2, column=0, padx=5, pady=3, sticky='w')
        self.label_stats4.grid(row=0, column=3, padx=5, pady=3, sticky="w") 
        self.label_stats5.grid(row=1, column=3, padx=5, pady=3, sticky="w")
        self.label_stats6.grid(row=2, column=3, padx=5, pady=3, sticky="w") 

        # Position value labels in right columns
        self.label_stats1_value.grid(row=0, column=1, padx=5, pady=3, sticky='e')
        self.label_stats2_value.grid(row=1, column=1, padx=5, pady=3, sticky='e')
        self.label_stats3_value.grid(row=2, column=1, padx=5, pady=3, sticky='e')
        self.label_stats4_value.grid(row=0, column=4, padx=5, pady=3, sticky="e") 
        self.label_stats5_value.grid(row=1, column=4, padx=5, pady=3, sticky="e")
        self.label_stats6_value.grid(row=2, column=4, padx=5, pady=3, sticky="e")

    def _setup_source_layout(self):
        """
        Configure the properties panel layout for Source appliances.
        """
        self._clear_stats_frame()
        
        # Configure labels for source appliance properties
        self.label_stats1.config(text="Power:")
        self.label_stats2.config(text="Duty Cycle:")
        self.label_stats3.config(text="Frequency:")
        self.label_stats4.config(text="Energy Generated:")
        self.label_stats5.config(text="Time Operated:")
        self.label_stats6.config(text="Fault:")

        # Position property labels in left columns
        self.label_stats1.grid(row=0, column=0, padx=5, pady=3, sticky='w')
        self.label_stats2.grid(row=1, column=0, padx=5, pady=3, sticky='w')
        self.label_stats3.grid(row=2, column=0, padx=5, pady=3, sticky='w')
        self.label_stats4.grid(row=0, column=3, padx=5, pady=3, sticky="w") 
        self.label_stats5.grid(row=1, column=3, padx=5, pady=3, sticky="w")
        self.label_stats6.grid(row=2, column=3, padx=5, pady=3, sticky="w") 

        # Position value labels in right columns
        self.label_stats1_value.grid(row=0, column=1, padx=5, pady=3, sticky='e')
        self.label_stats2_value.grid(row=1, column=1, padx=5, pady=3, sticky='e')
        self.label_stats3_value.grid(row=2, column=1, padx=5, pady=3, sticky='e')
        self.label_stats4_value.grid(row=0, column=4, padx=5, pady=3, sticky="e") 
        self.label_stats5_value.grid(row=1, column=4, padx=5, pady=3, sticky="e")
        self.label_stats6_value.grid(row=2, column=4, padx=5, pady=3, sticky="e")

    def _setup_storage_layout(self):
        """
        Configure the properties panel layout for Storage appliances.
        """
        self._clear_stats_frame()
        
        # Configure labels for storage appliance properties
        self.label_stats1.config(text="SOC:")
        self.label_stats2.config(text="Duty Cycle:")
        self.label_stats3.config(text="Frequency:")
        self.label_stats4.config(text="State:")
        self.label_stats5.config(text="Energy:")
        self.label_stats6.config(text="Fault:")

        # Position property labels in left columns
        self.label_stats1.grid(row=0, column=0, padx=5, pady=3, sticky='w')
        self.label_stats2.grid(row=1, column=0, padx=5, pady=3, sticky='w')
        self.label_stats3.grid(row=2, column=0, padx=5, pady=3, sticky='w')
        self.label_stats4.grid(row=0, column=3, padx=5, pady=3, sticky="w") 
        self.label_stats5.grid(row=1, column=3, padx=5, pady=3, sticky="w")
        self.label_stats6.grid(row=2, column=3, padx=5, pady=3, sticky="w") 

        # Position value labels in right columns
        self.label_stats1_value.grid(row=0, column=1, padx=5, pady=3, sticky='e')
        self.label_stats2_value.grid(row=1, column=1, padx=5, pady=3, sticky='e')
        self.label_stats3_value.grid(row=2, column=1, padx=5, pady=3, sticky='e')
        self.label_stats4_value.grid(row=0, column=4, padx=5, pady=3, sticky="e") 
        self.label_stats5_value.grid(row=1, column=4, padx=5, pady=3, sticky="e")
        self.label_stats6_value.grid(row=2, column=4, padx=5, pady=3, sticky="e")

    # Type-specific display update methods
    def _update_load_display(self, appliance):
        """
        Update display values for Load appliances.
        """
        # Calculate current electrical parameters
        current_power = appliance.get_current_power() if appliance.power_status else 0

        energy_used = getattr(appliance, 'energy_used', 0)  # Already in Wh
        
        # Format and display load appliance statistics
        self.label_stats1_value.config(text=f"{current_power:.1f} W")
        self.label_stats2_value.config(text=f"{appliance.pwm:.1f} %")
        self.label_stats3_value.config(text=f"{appliance.fm:.2f} kHz")
        self.label_stats4_value.config(text=f"{energy_used:.1f} Wh")
        self.label_stats5_value.config(text=f"{appliance.time_operated} sec")
        self.label_stats6_value.config(text="Fault" if appliance.fault else "No Fault")

    def _update_source_display(self, appliance):
        """
        Update display values for Source appliances.
        """
        # Calculate current electrical parameters
        current_power = appliance.get_current_power() if appliance.power_status else 0
        duty_cycle = getattr(appliance, 'pwm', 0)  # Duty cycle from PWM
        frequency = getattr(appliance, 'fm', 0)    # Frequency
        energy_generated = getattr(appliance, 'energy_used', 0)  # Already in Wh (for sources, this represents generated)
        
        # Format and display source appliance statistics
        self.label_stats1_value.config(text=f"{current_power:.1f} W")
        self.label_stats2_value.config(text=f"{duty_cycle:.1f} %")
        self.label_stats3_value.config(text=f"{frequency:.2f} kHz")
        self.label_stats4_value.config(text=f"{energy_generated:.1f} Wh")
        self.label_stats5_value.config(text=f"{appliance.time_operated} sec")
        self.label_stats6_value.config(text="Fault" if appliance.fault else "No Fault")

    def _update_storage_display(self, appliance):
        """
        Update display values for Storage appliances.
        """
        # Calculate storage-specific parameters
        capacity = getattr(appliance, 'capacity', 1000)  # Default capacity if not set
        energy_stored = getattr(appliance, 'energy_used', 0)  # Already in Wh
        soc = (energy_stored / capacity * 100) if capacity > 0 else 0  # State of Charge percentage
        
        duty_cycle = getattr(appliance, 'pwm', 0)  # Duty cycle from PWM
        frequency = getattr(appliance, 'fm', 0)    # Frequency
        
        # Determine storage state based on power flow
        current_power = appliance.get_current_power() if appliance.power_status else 0
        if current_power > 0:
            state = "Discharging"
        elif current_power < 0:
            state = "Charging"
        else:
            state = "Storing"
        
        # Format and display storage appliance statistics
        self.label_stats1_value.config(text=f"{soc:.1f} %")
        self.label_stats2_value.config(text=f"{duty_cycle:.1f} %")
        self.label_stats3_value.config(text=f"{frequency:.2f} kHz")
        self.label_stats4_value.config(text=state)
        self.label_stats5_value.config(text=f"{energy_stored:.1f} Wh")
        self.label_stats6_value.config(text="Fault" if appliance.fault else "No Fault")

    def update_appliance_display(self, appliance):
        """
        Update the properties panel if individual/summary appliance data is selected.
        """
        if isinstance(appliance, Appliance_Summary):
            # Display system-wide summary statistics
            self._update_summary_display(appliance)
        else:
            # Display individual appliance statistics
            self._update_individual_display(appliance)
    
    def _update_summary_display(self, appliance):
        """
        Update display for Appliance_Summary objects.
        """
        self.setup_summary_layout()
        
        # Format and display summary statistics
        self.label_stats1_value.config(
            text=f"{appliance.total_power_consumption:.1f} W"
        )
        self.label_stats2_value.config(
            text=f"{appliance.total_power_generation:.1f} W"
        )
        self.label_stats3_value.config(
            text=f"{appliance.total_energy_consumption:.3f} Wh"
        )
        self.label_stats4_value.config(
            text=f"{appliance.total_energy_generated:.3f} Wh"
        )
    
    def _update_individual_display(self, appliance):
        """
        Update display for individual appliance objects.
        Shows type-specific appliance metrics based on appliance type.
        """
        # Setup layout based on appliance type
        appliance_type = getattr(appliance, 'type', 0)
        
        if appliance_type == 0:  # Load
            self._setup_load_layout()
            self._update_load_display(appliance)
        elif appliance_type == 1:  # Source
            self._setup_source_layout()
            self._update_source_display(appliance)
        elif appliance_type == 2:  # Storage
            self._setup_storage_layout()
            self._update_storage_display(appliance)
        else:  # Default/Unknown type
            self._setup_load_layout()  # Default to load layout
            self._update_load_display(appliance)
