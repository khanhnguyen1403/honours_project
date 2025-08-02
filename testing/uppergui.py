from tkinter import *
from tkinter import ttk
from tkinter import messagebox as msgbox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import datetime


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
        self.option_clicked.set(appliance_names[1])
        self.option_clicked.trace("w", self.on_appliance_change)
        self.dropdown = OptionMenu(self.frame_appliance, self.option_clicked, *appliance_names)
        self.dropdown.config(width=20)

    def on_appliance_change(self, *args): #calls when dropdown changes
        self.update_power_button()
        
        # Update settings if settings frame is currently active
        if (hasattr(self, 'right_gui') and 
            hasattr(self.right_gui, 'current_frame') and 
            hasattr(self.right_gui, 'settings_frame') and
            self.right_gui.current_frame == getattr(self.right_gui, 'settings_frame', None)):
            # Settings frame is active, update it with new appliance
            self.right_gui.createSettings(self.root)
        
        # Update left GUI if it exists
        # if hasattr(self, 'left_gui'):
        #     self.left_gui.update_appliance_display(self.get_current_appliance())

    def get_current_appliance(self): #get object of current appliance
        current_appliance_name = self.option_clicked.get()
        return self.appliances.get(current_appliance_name)
    
    def update_power_button(self): #updates based on current selection
        current_appliance = self.get_current_appliance()
        if current_appliance is None:
            self.btn_power.config(text="", bg='gray', state='disabled')
            self.btn_settings.config(state='disabled')
            self.btn_logs.config(state='disabled')
            self.right_gui.createLogs(self.root)  # Reset logs frame
        else:
            self.btn_power.config(text=current_appliance.get_status_text(),
                                  bg=current_appliance.get_status_color(), state='normal')
            self.btn_settings.config(state='normal')

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
        if current_appliance.power_status:
            current_appliance.toggle_power()
            self.btn_power.config(text="OFF")
            self.btn_power.config(bg='red')
            self.right_gui.log_events(f"{current_name} turned OFF")
        else:
            current_appliance.toggle_power()
            self.btn_power.config(text="ON")    
            self.btn_power.config(bg='green')
            self.right_gui.log_events(f"{current_name} turned ON")

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
