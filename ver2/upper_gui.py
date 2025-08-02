from tkinter import *
from appliance import Appliance_Summary

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