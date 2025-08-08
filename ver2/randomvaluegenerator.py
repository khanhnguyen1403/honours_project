from tkinter import *
import random

class RandomValueGenerator: #testing purposes
    def __init__(self):
        self.variation_percent = {}  # Store variation percentages per appliance
    
    def set_appliance_variation(self, appliance_name, variation_percent=5):
        """Set variation percentage for an appliance"""
        self.variation_percent[appliance_name] = variation_percent
    
    def generate_value(self, appliance_name, appliance, is_on=True):
        if not is_on:
            return 0
            
        if appliance is None:
            return 0
        
        # Get current base power from appliance when generating value
        base_power = self._get_appliance_base_power(appliance)
        
        if base_power <= 0:
            return 0
        
        # Get variation percentage (default to 5% if not set)
        variation_percent = self.variation_percent.get(appliance_name, 5)
        variation = base_power * (variation_percent / 100)
        
        # Generate random value within variation range
        min_val = max(0, base_power - variation)
        max_val = base_power + variation
        
        return round(random.uniform(min_val, max_val), 1)
    
    def _get_appliance_base_power(self, appliance):
        """Get the appropriate base power value from an appliance based on its type"""
        if appliance.type == 0:  # Load
            return getattr(appliance, 'power_rating', 0)
        elif appliance.type == 1:  # Source
            return getattr(appliance, 'max_output_power', 0)
        elif appliance.type == 2:  # Storage
            return getattr(appliance, 'capacity', 0)
        else:
            return getattr(appliance, 'power_rating', 0)  # Default fallback
    
    def generate_summary_values(self, appliances_dict):
        """Generate summary values for the 'All' appliance"""
        total_consumption = 0
        total_generation = 0
        
        for name, appliance in appliances_dict.items():
            if name == "All" or appliance is None:
                continue
                
            if appliance.type == 0 and appliance.power_status:  # Load
                total_consumption += self.generate_value(name, appliance, appliance.power_status)
            elif appliance.type == 1 and appliance.power_status:  # Source
                total_generation += self.generate_value(name, appliance, appliance.power_status)
        
        return total_consumption, total_generation