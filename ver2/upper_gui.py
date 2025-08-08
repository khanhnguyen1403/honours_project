from tkinter import *
from tkinter import Toplevel
from appliance import Appliance_Summary


class Upper_GUI:
    """
    Upper GUI class manages the main control interface for appliance selection and power control.
    Provides appliance dropdown selection, power toggle button, and view switching (logs/settings).
    """
    
    def __init__(self, root, right_gui, appliances):
        """
        Initialize the upper GUI with control elements and appliance management.
        """
        self.root = root
        self.right_gui = right_gui
        self.appliances = appliances

        # Create main control frames
        self._create_frames()
        
        # Initialize UI components
        self._initialize_components()
        
        # Setup initial state and display
        self.update_power_button()
        self.publish()

    def _create_frames(self):
        """Create the main labeled frames for the upper GUI sections."""
        self.frame_appliance = LabelFrame(self.root, text="Appliance", padx=5, pady=5, bg="white")
        self.frame_power = LabelFrame(self.root, text="Power", padx=5, pady=5, bg="white")
        self.frame_options = LabelFrame(self.root, text="Options", padx=5, pady=5, bg="white")

    def _initialize_components(self):
        """Initialize all UI components."""
        # Create appliance selection dropdown
        self.OptionMenu()
        
        # Create power control button
        self.btn_power = Button(self.frame_power, text="OFF", bg='red', width=10, command=self.command_switch_power)
        
        # Create view switching buttons
        self.btn_logs = Button(self.frame_options, text="Logs", width=10, command=self.command_logs, state='disabled')  # Start with logs view active
        self.btn_settings = Button(self.frame_options, text="Settings", width=10, command=self.command_settings)

    def OptionMenu(self):
        """
        Create the appliance selection dropdown menu.
        Sets up the dropdown with all available appliances and change detection.
        """
        # Get list of all appliance names
        appliance_names = list(self.appliances.keys())
        
        # Add "Add appliance..." option at the end
        appliance_names.append("Add appliance...")
        
        # Create StringVar for dropdown selection tracking
        self.option_clicked = StringVar(self.root)
        self.option_clicked.set(appliance_names[1])  # Set to first real appliance (skip "All")
        
        # Add trace to detect dropdown changes
        self.option_clicked.trace("w", self.on_appliance_change)
        
        # Create dropdown menu widget
        self.dropdown = OptionMenu(self.frame_appliance, self.option_clicked, *appliance_names)
        self.dropdown.config(width=20)

    def on_appliance_change(self, *args):
        """
        Handle appliance selection changes in the dropdown.
        Updates GUI state, manages view switching, and refreshes displays.
        """
        # Check if "Add appliance..." was selected
        selected_option = self.option_clicked.get()
        if selected_option == "Add appliance...":
            self._handle_add_appliance()
            return
        
        # Store current view state to maintain user's preferred view
        current_view_state = self._get_current_view_state()
        
        # Update summary appliance data if it exists
        self._update_summary_appliance()
        
        # Get the newly selected appliance
        new_appliance = self.get_current_appliance()
        
        # Update power button appearance
        self.update_power_button()
        
        # Handle view switching based on appliance type
        self._handle_view_switching(new_appliance, current_view_state)
        
        # Update left GUI displays
        self._update_left_gui_displays(new_appliance)

    def _get_current_view_state(self):
        """
        Determine the current view state (settings or logs).
        """
        is_settings = (
            hasattr(self, 'right_gui') and 
            hasattr(self.right_gui, 'current_frame') and 
            hasattr(self.right_gui, 'settings_frame') and
            self.right_gui.current_frame == getattr(self.right_gui, 'settings_frame', None)
        )
        
        is_logs = (
            hasattr(self, 'right_gui') and 
            hasattr(self.right_gui, 'current_frame') and 
            hasattr(self.right_gui, 'log_frame') and
            self.right_gui.current_frame == getattr(self.right_gui, 'log_frame', None)
        )
        
        return {'is_settings': is_settings, 'is_logs': is_logs}

    def _update_summary_appliance(self):
        """Update the 'All' summary appliance with current data from all appliances."""
        if "All" in self.appliances and isinstance(self.appliances["All"], Appliance_Summary):
            self.appliances["All"].update_from_appliances(self.appliances)

    def _handle_view_switching(self, new_appliance, current_view_state):
        """
        Handle view switching logic based on appliance type and current view state.
        """
        if isinstance(new_appliance, Appliance_Summary):
            # Switching to 'All' summary view - always show logs, disable settings
            self.right_gui.createLogs(self.root)
            self.btn_logs.config(state='disabled')
            self.btn_settings.config(state='disabled')  # No settings for summary
        else:
            # Switching to individual appliance - maintain previous view if possible
            self._switch_to_individual_appliance_view(current_view_state)

    def _switch_to_individual_appliance_view(self, current_view_state):
        """
        Switch to individual appliance view, maintaining user's preferred view.
        """
        if current_view_state['is_settings']:
            # Maintain settings view
            self.right_gui.createSettings(self.root)
            self.btn_settings.config(state='disabled')
            self.btn_logs.config(state='normal')
        elif current_view_state['is_logs']:
            # Maintain logs view
            self.right_gui.createLogs(self.root)
            self.btn_logs.config(state='disabled')
            self.btn_settings.config(state='normal')
        else:
            # Default to logs view if state is unclear
            self.right_gui.createLogs(self.root)
            self.btn_logs.config(state='disabled')
            self.btn_settings.config(state='normal')

    def _update_left_gui_displays(self, new_appliance):
        """
        Update left GUI displays with new appliance data.
        """
        if hasattr(self, 'left_gui'):
            self.left_gui.update_appliance_display(new_appliance)
            self.left_gui.update_graph(new_appliance)

    def _handle_add_appliance(self):
        """
        Handle the "Add appliance..." option selection.
        """
        # Create popup window for appliance name input
        popup = Toplevel(self.root)
        popup.title("Add New Appliance")
        popup.geometry("200x100")
        popup.resizable(False, False)
        
        # Center the popup window
        popup.transient(self.root)
        popup.grab_set()
        
        # Create input form
        Label(popup, text="Enter Appliance Name:").pack(pady=5)

        name_entry = Entry(popup, width=20)
        name_entry.pack(pady=5)
        name_entry.focus()
        
        # Button frame
        button_frame = Frame(popup)
        button_frame.pack(pady=5)
        
        def create_appliance():
            appliance_name = name_entry.get().strip()
            if appliance_name:
                if appliance_name in self.appliances:
                    # Show error if name already exists
                    error_label.config(text="Appliance name already exists!", fg="red")
                    return
                
                # Create new appliance with next available ID
                new_id = self._get_next_appliance_id()
                new_appliance = self._create_new_appliance(appliance_name, new_id)
                
                # Add to appliances dictionary
                self.appliances[appliance_name] = new_appliance
                
                # Refresh dropdown menu
                self._refresh_dropdown_menu()
                
                # Select the new appliance
                self.option_clicked.set(appliance_name)
                
                # Clear displays and show settings for new appliance
                self._setup_new_appliance_display(new_appliance)
                
                popup.destroy()
            else:
                error_label.config(text="Please enter a valid name", fg="red")
        
        def cancel_creation():
            # Reset to previous selection (first real appliance)
            appliance_names = [name for name in self.appliances.keys() if name != "All"]
            if appliance_names:
                self.option_clicked.set(appliance_names[0])
            popup.destroy()
        
        # Create buttons
        Button(button_frame, text="Create", command=create_appliance, 
               bg="green", fg="white", width=10).pack(side=LEFT, padx=5)
        Button(button_frame, text="Cancel", command=cancel_creation, 
               width=10).pack(side=LEFT, padx=5)
        
        # Error message label
        error_label = Label(popup, text="", fg="red")
        error_label.pack()
        
        # Handle Enter key to create appliance and Escape key to cancel
        def handle_enter(event):
            create_appliance()
        
        def handle_escape(event):
            cancel_creation()
        
        # Bind keyboard events
        popup.bind('<Return>', handle_enter)
        name_entry.bind('<Return>', handle_enter)

    def _get_next_appliance_id(self):
        """
        Get the next available ID for a new appliance.
        """
        used_ids = []
        for appliance in self.appliances.values():
            if hasattr(appliance, 'ID') and appliance.ID != 0:  # Skip "All" (ID=0)
                used_ids.append(appliance.ID)
        
        return max(used_ids) + 1 if used_ids else 1

    def _create_new_appliance(self, name, appliance_id):
        """
        Create a new appliance object with default settings.
        """
        from appliance import Appliance
        new_appliance = Appliance(name, appliance_id)
        
        # Set default values (these can be customized in settings)
        new_appliance.type = 0  # Default to load
        
        return new_appliance

    def _refresh_dropdown_menu(self):
        """
        Refresh the dropdown menu to include newly added appliances.
        """
        # Get updated appliance names
        appliance_names = list(self.appliances.keys())
        appliance_names.append("Add appliance...")
        
        # Destroy old dropdown and create new one
        self.dropdown.destroy()
        self.dropdown = OptionMenu(self.frame_appliance, self.option_clicked, *appliance_names)
        self.dropdown.config(width=20)
        self.dropdown.grid(row=2, column=0, padx=5, pady=5)

    def _setup_new_appliance_display(self, new_appliance):
        """
        Set up displays for the newly created appliance.
        Clear graphs and show settings for configuration.
        """
        # Clear and update left GUI displays
        if hasattr(self, 'left_gui'):
            self.left_gui.update_appliance_display(new_appliance)
            self.left_gui.update_graph(new_appliance)
        
        # Switch to settings view for new appliance configuration
        self.right_gui.createSettings(self.root)
        self.btn_settings.config(state='disabled')
        self.btn_logs.config(state='normal')
        
        # Update power button for new appliance
        self.update_power_button()

    def get_current_appliance(self):
        """
        Get the currently selected appliance object from the dropdown.
        """
        current_appliance_name = self.option_clicked.get()
        return self.appliances.get(current_appliance_name)
    
    def update_power_button(self):
        """
        Update the power button appearance and state based on current appliance selection.
        Handles different states: no selection, summary view, and individual appliances.
        """
        current_appliance = self.get_current_appliance()
        
        if current_appliance is None:
            # No valid appliance selected
            self._set_power_button_disabled()
            self._disable_all_option_buttons()
            self.right_gui.createLogs(self.root)  # Reset to logs view
        elif isinstance(current_appliance, Appliance_Summary):
            # Summary appliance - disable power control
            self._set_power_button_summary()
        else:
            # Individual appliance - enable power control with current status
            self._set_power_button_for_appliance(current_appliance)

    def _set_power_button_disabled(self):
        """Configure power button for disabled state (no appliance)."""
        self.btn_power.config(text="", bg='gray', state='disabled')

    def _set_power_button_summary(self):
        """Configure power button for summary view (disabled)."""
        self.btn_power.config(text="--", bg='gray', state='disabled')
        

    def _set_power_button_for_appliance(self, appliance):
        """
        Configure power button for individual appliance.
        """
        self.btn_power.config(
            text=appliance.get_status_text(),
            bg=appliance.get_status_color(), 
            state='normal'
        )

    def _disable_all_option_buttons(self):
        """Disable both logs and settings buttons."""
        self.btn_settings.config(state='disabled')
        self.btn_logs.config(state='disabled')
        
    def publish(self):
        """
        Arrange and display all GUI components using grid layout.
        Configures the positioning and layout of frames and buttons.
        """
        # Position main frames
        self.frame_appliance.grid(row=0, column=0, rowspan=3, columnspan=3, padx=5, pady=5)    
        self.frame_power.grid(row=0, column=3, rowspan=3, columnspan=3, padx=5, pady=5, sticky='e')

        # Configure grid weight for proper resizing
        self.root.grid_columnconfigure(6, weight=1) 
        
        self.frame_options.grid(row=0, column=6, rowspan=3, padx=5, pady=5, sticky='e') 
        
        # Position components within frames
        self.dropdown.grid(row=2, column=0, padx=5, pady=5)
        self.btn_power.grid(row=2, column=4, padx=5, pady=7)
        
        # Position option buttons
        self.btn_logs.grid(row=1, column=5, padx=5, pady=3, sticky='e') 
        self.btn_settings.grid(row=1, column=6, padx=5, pady=3, sticky='e') 

    def command_switch_power(self):
        """
        Handle power button click to toggle appliance power state.
        Updates appliance status, logs the change, and refreshes displays.
        """
        current_appliance = self.get_current_appliance()
        current_name = self.option_clicked.get()
        
        if current_appliance.power_status:
            # Turning OFF - immediate response
            current_appliance.toggle_power()
            self.right_gui.log_events(f"{current_name} turned OFF")
            
            # Update summary appliance and displays immediately
            self._update_summary_appliance()
            self.update_power_button()
            self._update_current_appliance_display(current_appliance)
        else:
            # Turning ON - show "Starting..." for 3 seconds
            self._handle_power_on_sequence(current_appliance, current_name)

    def _update_current_appliance_display(self, appliance):
        """
        Update the left GUI display for the current appliance.
        """
        if hasattr(self, 'left_gui'):
            self.left_gui.update_appliance_display(appliance)

    def _handle_power_on_sequence(self, appliance, appliance_name):
        """
        Handle the power-on sequence with 3-second "Starting..." delay.
        """
        # Set button to "Starting..." state and disable it
        self.btn_power.config(text="Starting...", bg='orange', state='disabled')
        
        # Schedule the actual power-on after 3 seconds
        self.root.after(3000, lambda: self._complete_power_on(appliance, appliance_name))

    def _complete_power_on(self, appliance, appliance_name):
        """
        Complete the power-on sequence after the delay.
        """
        # Actually turn on the appliance
        appliance.toggle_power()
        
        # Log the completion
        self.right_gui.log_events(f"{appliance_name} turned ON")
        
        # Update summary appliance and displays
        self._update_summary_appliance()
        self.update_power_button()
        self._update_current_appliance_display(appliance)

    def command_logs(self):
        """
        Switch to logs view and update button states.
        Disables logs button and enables settings button.
        """
        self.right_gui.createLogs(self.root)
        self.btn_logs.config(state='disabled')  # Disable current view button
        self.btn_settings.config(state='normal')  # Enable alternate view button

    def command_settings(self):
        """
        Switch to settings view and update button states.
        Disables settings button and enables logs button.
        """
        self.right_gui.createSettings(self.root)
        self.btn_settings.config(state='disabled')  # Disable current view button
        self.btn_logs.config(state='normal')  # Enable alternate view button