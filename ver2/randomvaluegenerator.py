from tkinter import *
from tkinter import ttk
from tkinter import messagebox as msgbox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import datetime
import random
import time
from datetime import datetime, timedelta
import matplotlib.dates as mdates


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