from tkinter import *
from tkinter import messagebox as msgbox
import datetime
from appliance import Appliance_Summary
from datetime import datetime


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
                # Check if appliance is ON before allowing settings to be saved
                if current_appliance.power_status:
                    msgbox.showwarning("Cannot Save Settings", 
                                     f"Cannot save settings for '{current_appliance.name}' while it is ON. "
                                     f"Turn off the appliance.")
                    return
                
                self.update_appliance_properties(current_appliance, selected_type, settings_data)
                
                # Log the saved settings with appliance name
                self.log_events(f"Settings saved for {current_appliance.name} ({selected_type})")
                # Show confirmation with appliance name
                msgbox.showinfo("Settings Saved", 
                              f"Settings for '{current_appliance.name}' have been saved successfully!")
            else:
                msgbox.showwarning("Cannot Save")
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

