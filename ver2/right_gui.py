from tkinter import *
from tkinter import messagebox as msgbox
import datetime
from appliance import Appliance_Summary
from datetime import datetime


class Right_GUI:
    """
    Right GUI class manages the logs display and appliance settings configuration.
    Provides settings forms based on appliance type and maintains event logging.
    """ 
    def __init__(self, root, upper_gui=None):
        """
        Initialize the Right GUI component.
        """
        self.root = root
        self.upper_gui = upper_gui
        self.current_frame = None
        self.log_data = []  # Store persistent log data
        
        # Initialize with logs frame as default view
        self.createLogs(root)

    def createLogs(self, root):
        """
        Create and display the logs frame with scrollable text area.
        Destroys any existing frame and sets up event logging display.
        """
        # Remove current frame if it exists
        if self.current_frame:
            self.current_frame.destroy()
            
        # Create logs frame
        self.log_frame = LabelFrame(root, text="Logs", padx=5,  pady=3, bg="white")
        self.log_frame.grid(row=4, column=6, rowspan=4, padx=5, pady=3, sticky='nsew')
        
        # Set as current active frame
        self.current_frame = self.log_frame

        # Create scrollbar for log text area
        self.scrollbar = Scrollbar(self.log_frame)
        self.scrollbar.grid(row=0, column=1, sticky='ns') 

        # Create text widget for displaying logs
        self.log_textbox = Text(self.log_frame,  bg='white', wrap="word", state="disabled", yscrollcommand=self.scrollbar.set)
        self.log_textbox.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights for proper resizing
        self.log_frame.grid_rowconfigure(0, weight=1)
        self.log_frame.grid_columnconfigure(0, weight=1)

        # Link scrollbar to text widget
        self.scrollbar.config(command=self.log_textbox.yview)

        # Restore any existing log data
        self.restore_logs()

    def createSettings(self, root):
        """
        Create and display the settings frame with dynamic appliance configuration.
        Switches from logs view to settings view and sets up appliance type selection.
        """
        # Remove current frame
        if self.current_frame:
            self.current_frame.destroy()
            
        # Create settings frame
        self.settings_frame = LabelFrame(root, text="Settings", padx=5, pady=3, bg="white")
        self.settings_frame.grid(row=4, column=6, rowspan=5, padx=5, pady=3, sticky='nsew')

        # Set as current active frame
        self.current_frame = self.settings_frame
        
        # Setup appliance type selection
        self._create_type_selection()
        
        # Store current appliance reference for settings
        self.current_appliance_for_settings = self._get_current_appliance()
        
        # Create dynamic settings based on selected type
        self.create_dynamic_settings()

    def _create_type_selection(self):
        """
        Create the appliance type selection dropdown.
        Sets the initial type based on the currently selected appliance.
        """
        # Create appliance type label
        self.setting1 = Label(self.settings_frame, text="Appliance Type:", bg="white")
        self.setting1.grid(row=1, column=0, padx=5, pady=5, sticky='w')
        
        # Define available appliance types
        appliance_types = ["Load", "Source", "Storage"]
        self.selected_type = StringVar(self.settings_frame)
        
        # Set initial type based on current appliance
        self._set_initial_appliance_type(appliance_types)
        
        # Add trace to detect type changes
        self.selected_type.trace('w', self.on_type_change)
        
        # Create dropdown menu
        self.dropdown1 = OptionMenu(
            self.settings_frame, 
            self.selected_type, 
            *appliance_types
        )
        self.dropdown1.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        self.dropdown1.config(width=15)

    def _get_current_appliance(self):
        """
        Get the currently selected appliance from the upper GUI.
        """
        if self.upper_gui:
            return self.upper_gui.get_current_appliance()
        return None

    def _set_initial_appliance_type(self, appliance_types):
        """
        Set the initial appliance type selection based on current appliance.
        """
        current_appliance = self._get_current_appliance()
        
        if (current_appliance is not None and 
            not isinstance(current_appliance, Appliance_Summary)):
            # Set type based on appliance's stored type
            type_mapping = {0: "Load", 1: "Source", 2: "Storage"}
            appliance_type = type_mapping.get(current_appliance.type, appliance_types[0])
            self.selected_type.set(appliance_type)
        else:
            # Default to first type for "All" view or no selection
            self.selected_type.set(appliance_types[0])

    def on_type_change(self, *args):
        """
        Handle appliance type dropdown change events.
        Updates the current appliance reference and recreates dynamic settings.
        """
        # Update the current appliance reference when type changes
        if self.upper_gui:
            self.current_appliance_for_settings = self.upper_gui.get_current_appliance()
        
        # Recreate settings form with new type
        self.create_settings()

    def create_settings(self):
        """
        Create settings form based on selected appliance type.
        """
        # Clear existing widgets if they exist
        self._clear_widgets()
        
        # Initialize storage for new widgets and entries
        self.dynamic_widgets = []
        self.setting_entries = {}  # Store entry widgets for value access
        
        selected_type = self.selected_type.get()
        current_appliance = getattr(self, 'current_appliance_for_settings', None)
        
        # Handle summary appliance case (no settings available)
        if isinstance(current_appliance, Appliance_Summary):
            self._create_summary_message()
            return
        
        # Create settings based on appliance type
        settings = self._get_settings_for_type(selected_type, current_appliance)
        self._create_settings_widgets(settings)
        self._create_save_button(len(settings))
        
        # Configure grid weights for proper resizing
        self.settings_frame.grid_columnconfigure(1, weight=1)

    def _clear_widgets(self):
        """Clear all existing widgets from the settings frame."""
        if hasattr(self, 'dynamic_widgets'):
            for widget in self.dynamic_widgets:
                widget.destroy()

    def _get_settings_for_type(self, selected_type, current_appliance):
        """
        Get settings configuration for the specified appliance type.
        """
        if selected_type == "Load":
            return self._get_load_settings(current_appliance)
        elif selected_type == "Source":
            return self._get_source_settings(current_appliance)
        else:  # Storage
            return self._get_storage_settings(current_appliance)

    def _get_load_settings(self, current_appliance):
        """
        Get settings configuration for Load type appliances.
        """
        if current_appliance and current_appliance.type == 0:
            return [
                ("Rated Power (W):", 
                 str(current_appliance.power_rating) if current_appliance.power_rating > 0 else ""),
                ("Rated Voltage (V):", 
                 str(current_appliance.voltage_rating) if current_appliance.voltage_rating > 0 else ""),
                ("Frequency Modulation (kHz):", 
                 str(current_appliance.fm) if current_appliance.fm > 0 else ""),
                ("Overvoltage Threshold (V):", 
                 str(current_appliance.overvoltage_threshold) if current_appliance.overvoltage_threshold > 0 else ""),
                ("Undervoltage Threshold (V):", 
                 str(current_appliance.undervoltage_threshold) if current_appliance.undervoltage_threshold > 0 else ""),
                ("Differential Threshold (A):", 
                 str(current_appliance.differential_threshold) if current_appliance.differential_threshold > 0 else ""),
            ]
        else:
            return [
                ("Rated Power (W):", ""),
                ("Rated Voltage (V):", ""),
                ("Frequency Modulation (kHz):", ""),
                ("Overvoltage Threshold (V):", ""),
                ("Undervoltage Threshold (V):", ""),
                ("Differential Threshold (A):", ""),
            ]

    def _get_source_settings(self, current_appliance):
        """
        Get settings configuration for Source type appliances.
        """
        if current_appliance and current_appliance.type == 1:
            return [
                ("Max Output Power (W):", 
                 str(current_appliance.max_output_power) if current_appliance.max_output_power > 0 else ""),
                ("Output Voltage (V):", 
                 str(current_appliance.voltage_rating) if current_appliance.voltage_rating > 0 else ""),
                ("Frequency Modulation (kHz):", 
                 str(current_appliance.fm) if current_appliance.fm > 0 else ""),
                ("Undervoltage Threshold (V):", 
                 str(current_appliance.undervoltage_threshold) if current_appliance.undervoltage_threshold > 0 else ""),
            ]
        else:
            return [
                ("Max Output Power (W):", ""),
                ("Output Voltage (V):", ""),
                ("Frequency Modulation (kHz):", ""),
                ("Undervoltage Threshold (V):", ""),
            ]

    def _get_storage_settings(self, current_appliance):
        """
        Get settings configuration for Storage type appliances.
        """
        if current_appliance and current_appliance.type == 2:
            return [
                ("Capacity (Wh):", 
                 str(current_appliance.capacity) if current_appliance.capacity > 0 else ""),
                ("Rated Voltage (V):", 
                 str(current_appliance.voltage_rating) if current_appliance.voltage_rating > 0 else ""),
                ("Discharge Frequency Modulation (kHz):", 
                 str(current_appliance.fm_discharge) if current_appliance.fm_discharge > 0 else ""),
                ("Charging Frequency Modulation (kHz):", 
                 str(current_appliance.fm_charge) if current_appliance.fm_charge > 0 else ""),
            ]
        else:
            return [
                ("Capacity (Wh):", ""),
                ("Rated Voltage (V):", ""),
                ("Max Charge Current (A):", ""),
                ("Max Discharge Current (A):", ""),
            ]

    def _create_settings_widgets(self, settings):
        """
        Create label and entry widgets for each setting.
        """
        for i, (label_text, default_value) in enumerate(settings):
            row = i + 2  # Start from row 2 (after appliance type)
            
            # Create and position label
            label = Label(self.settings_frame, text=label_text, bg="white")
            label.grid(row=row, column=0, padx=5, pady=3, sticky='w')
            self.dynamic_widgets.append(label)
            
            # Create and position entry with default value
            entry = Entry(self.settings_frame)
            entry.insert(0, default_value)  # Set saved value or empty string
            self.setting_entries[f'setting_{i}'] = entry
            
            entry.grid(row=row, column=1, padx=5, pady=3, sticky='ew')
            self.dynamic_widgets.append(entry)

    def _create_save_button(self, num_settings):
        """
        Create the save settings button at the bottom of the form.
        """
        save_row = num_settings + 2
        self.btn_save_data = Button(
            self.settings_frame, 
            text="Save Settings", 
            width=15, 
            command=self.save_settings,
            bg='lightblue', 
            cursor='hand2'
        )
        self.btn_save_data.grid(
            row=save_row, column=0, columnspan=2, 
            padx=5, pady=10
        )
        self.dynamic_widgets.append(self.btn_save_data)

    def save_settings(self):
        """
        Save the current settings form data to the selected appliance.
        Validates that the appliance is turned off before allowing saves.
        Displays appropriate success/error messages and logs the operation.
        """
        selected_type = self.selected_type.get()
        settings_data = self._collect_settings_data()
        
        # Get the current appliance from Upper_GUI
        current_appliance = self._get_current_appliance()
        
        if current_appliance is not None and not isinstance(current_appliance, Appliance_Summary):
            # Validate appliance is OFF before allowing settings changes
            if current_appliance.power_status:
                msgbox.showwarning(
                    "Cannot Save Settings", 
                    f"Cannot save settings for '{current_appliance.name}' while it is ON. "
                    f"Turn off the appliance first."
                )
                return
            
            # Update appliance properties with new settings
            self.update_appliance_properties(current_appliance, selected_type, settings_data)
            
            # Log the successful save operation
            self.log_events(f"Settings saved for {current_appliance.name} ({selected_type})")
            
            # Show success confirmation
            msgbox.showinfo(
                "Settings Saved", 
                f"Settings for '{current_appliance.name}' have been saved successfully!"
            )
        else:
            # Handle case where no valid appliance is selected
            msgbox.showwarning("Cannot Save", "No valid appliance selected for settings.")

    def _collect_settings_data(self):
        """
        Collect all settings data from the form entries.
        """
        settings_data = {}
        
        # Get all entry values
        for key, widget in self.setting_entries.items():
            if isinstance(widget, Entry):
                settings_data[key] = widget.get()
            elif isinstance(widget, StringVar):
                settings_data[key] = widget.get()
        
        return settings_data

    def update_appliance_properties(self, appliance, appliance_type, settings_data):
        """
        Update appliance properties based on types and the settings form data.
        """
        # Set appliance type code
        type_mapping = {"Load": 0, "Source": 1, "Storage": 2}
        appliance.type = type_mapping.get(appliance_type, 0)
        
        # Update properties based on appliance type
        if appliance_type == "Load":
            self._update_load_properties(appliance, settings_data)
        elif appliance_type == "Source":
            self._update_source_properties(appliance, settings_data)
        elif appliance_type == "Storage":
            self._update_storage_properties(appliance, settings_data)
        
        # Log successful update
        self.log_events(f"Appliance '{appliance.name}' properties updated successfully")

    def _update_load_properties(self, appliance, settings_data):
        """
        Update properties specific to Load type appliances.
        """
        property_mapping = {
            'setting_0': ('power_rating', 'Rated Power (W)'),
            'setting_1': ('voltage_rating', 'Rated Voltage (V)'),
            'setting_2': ('max_current', 'Max Current (A)'),
            'setting_3': ('overvoltage_threshold', 'Overvoltage Threshold (V)'),
            'setting_4': ('undervoltage_threshold', 'Undervoltage Threshold (V)'),
            'setting_5': ('differential_threshold', 'Differential Threshold (A)'),
        }
        
        self._apply_property_updates(appliance, settings_data, property_mapping)

    def _update_source_properties(self, appliance, settings_data):
        """
        Update properties specific to Source type appliances.
        """
        property_mapping = {
            'setting_0': ('max_output_power', 'Max Output Power (W)'),
            'setting_1': ('voltage_rating', 'Output Voltage (V)'),
            'setting_2': ('max_output_current', 'Max Output Current (A)'),
            'setting_3': ('undervoltage_threshold', 'Undervoltage Threshold (V)'),
        }
        
        self._apply_property_updates(appliance, settings_data, property_mapping)

    def _update_storage_properties(self, appliance, settings_data):
        """
        Update properties specific to Storage type appliances.
        """
        property_mapping = {
            'setting_0': ('capacity', 'Capacity (Wh)'),
            'setting_1': ('voltage_rating', 'Rated Voltage (V)'),
            'setting_2': ('max_charge_current', 'Max Charge Current (A)'),
            'setting_3': ('max_discharge_current', 'Max Discharge Current (A)'),
        }
        
        self._apply_property_updates(appliance, settings_data, property_mapping)

    def _apply_property_updates(self, appliance, settings_data, property_mapping):
        """
        Apply property updates to an appliance using the provided mapping.
        
        Args:
            appliance: The appliance object to update
            settings_data: Dictionary containing form field values
            property_mapping: Dictionary mapping setting keys to (property_name, display_name)
        """
        for key, (property_name, display_name) in property_mapping.items():
            value = settings_data.get(key, "")
            
            if not value:  # Skip empty values
                continue
                
            try:
                # Convert to float and set property
                setattr(appliance, property_name, float(value))
            except ValueError:
                # Log warning for invalid values
                self.log_events(f"Warning: Invalid value '{value}' for {display_name}")
        
        # Log successful update - moved to parent method to avoid duplication
        
    def log_events(self, message):
        """
        Add a timestamped event to the log display and persistent storage.
        """
        # Create timestamped log entry
        timestamp = datetime.now().strftime("%d/%m %H:%M:%S")
        entry = f"[{timestamp}] {message}\n"
        
        # Store in persistent log data
        self.log_data.append(entry)
        
        # Display in log textbox if it exists and is valid
        if (hasattr(self, 'log_textbox') and 
            self.log_textbox.winfo_exists()):
            self.log_textbox.configure(state="normal")
            self.log_textbox.insert("end", entry)
            self.log_textbox.configure(state="disabled")
            self.log_textbox.see("end")  # Auto-scroll to bottom

    def restore_logs(self):
        """
        Restore all persistent log data to the log textbox display.
        Called when switching back to logs view or initializing the log display.
        """
        if hasattr(self, 'log_textbox') and self.log_data:
            # Clear existing content
            self.log_textbox.configure(state="normal")
            self.log_textbox.delete("1.0", "end")
            
            # Restore all log entries
            for entry in self.log_data:
                self.log_textbox.insert("end", entry)
            
            # Set back to read-only and scroll to bottom
            self.log_textbox.configure(state="disabled")
            self.log_textbox.see("end")

