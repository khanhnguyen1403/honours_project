from tkinter import *
import threading
import time


class DataUpdateManager:
    def __init__(self, appliances, value_generator, left_gui, right_gui):
        self.appliances = appliances
        self.value_generator = value_generator
        self.left_gui = left_gui
        self.right_gui = right_gui
        self.running = False
        self.update_thread = None
        
    def start_updates(self):
        """Start the data update thread"""
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
    def stop_updates(self):
        """Stop the data update thread"""
        self.running = False
        
    def _update_loop(self):
        """Main update loop that runs every second"""
        while self.running:
            try:
                # Update individual appliances
                for name, appliance in self.appliances.items():
                    if name == "All" or appliance is None:
                        continue
                        
                    # Generate new power value
                    new_power = self.value_generator.generate_value(name, appliance.power_status)
                    appliance.update_power_value(new_power)
                
                # Update summary appliance
                if "All" in self.appliances:
                    summary = self.appliances["All"]
                    consumption, generation = self.value_generator.generate_summary_values(self.appliances)
                    summary.update_power_value(consumption, generation)
                    summary.update_from_appliances(self.appliances)
                
                # Update GUI in main thread
                self.left_gui.root.after(0, self._update_gui)
                
                # Wait for 1 second
                time.sleep(1)
                
            except Exception as e:
                print(f"Error in update loop: {e}")
                
    def _update_gui(self):
        """Update GUI elements (called in main thread)"""
        try:
            # Refresh the graph for currently displayed appliance
            self.left_gui.refresh_current_graph()
            
            # Update properties display for current appliance
            if hasattr(self.left_gui, 'current_appliance') and self.left_gui.current_appliance:
                self.left_gui.update_appliance_display(self.left_gui.current_appliance)
                
        except Exception as e:
            print(f"Error updating GUI: {e}")

