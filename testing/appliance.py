class Appliance:
    def __init__(self, name, ID):
        self.name = name
        self.power_status = False
        self.ID = ID
        
        # Initialize all possible properties
        self.type = 0  # 0: load, 1: source, 2: storage
        self.voltage_rating = 0
        self.power_rating = 0
        self.power = 0
        self.voltage = 0
        self.current = 0
        self.energy_used = 0
        self.time_operated = 0
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

    def properties(self):
        # This method can be used to return all properties as a dictionary
        return {
            'name': self.name,
            'type': self.type,
            'power_status': self.power_status,
            'voltage_rating': self.voltage_rating,
            'power_rating': self.power_rating,
            'power': self.power,
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

    def get_status_text(self):
        return "ON" if self.power_status else "OFF"
    
    def get_status_color(self):
        return 'green' if self.power_status else 'red'