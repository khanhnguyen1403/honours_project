#Class representing a load 
class DeviceData:
    def __init__(self, deviceName, averageVoltage = 0.0, averageCurrent = 0.0):
        self.deviceName = deviceName
        self.averageVoltage = averageVoltage
        self.averageCurrent = averageCurrent

    def setVoltage(self, averageVoltage):
        self.averageVoltage = averageVoltage
    
    def setCurrent(self, averageCurrent):
        self.averageCurrent = averageCurrent

    def get_voltage(self):
        return self.averagevoltage
    
    def get_current(self):
        return self.averageCurrent
    
    def calculate_power(self):
        return self.averageVoltage * self.averageCurrent
    
    def updateData(self, voltage, current):
        self.set_voltage(voltage)
        self.set_current(current)
    
    def returnData(self):
        return (f"Device: {self.device_name}, "
                f"Voltage: {self.voltage} V, "
                f"Current: {self.current} A, "
                f"Power: {self.calculate_power()} W")      
