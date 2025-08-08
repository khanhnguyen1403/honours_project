from tkinter import *
import threading
import time
from datetime import datetime, timedelta
from excel_exporter import ExcelExporter


class DataUpdateManager:
    """Manages the real-time data updates for all appliances"""
    def __init__(self, appliances, value_generator, left_gui, right_gui):
        self.appliances = appliances
        self.value_generator = value_generator
        self.left_gui = left_gui
        self.right_gui = right_gui
        self.running = False
        self.update_thread = None
        
        # Give right_gui access to value_generator for settings updates
        self.right_gui.value_generator = value_generator
        
        # Excel export functionality
        self.excel_exporter = ExcelExporter(appliances, right_gui)
        self.last_export_time = None
        
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
                current_time = datetime.now()
                
                # Update individual appliances
                for name, appliance in self.appliances.items():
                    if name == "All" or appliance is None:
                        continue
                        
                    # Generate new power value (pass appliance object so it can check current ratings)
                    new_power = self.value_generator.generate_value(name, appliance, appliance.power_status)
                    appliance.update_power_value(new_power)
                
                # Update summary appliance
                if "All" in self.appliances:
                    summary = self.appliances["All"]
                    consumption, generation = self.value_generator.generate_summary_values(self.appliances)
                    summary.update_power_value(consumption, generation)
                    summary.update_from_appliances(self.appliances)
                
                # Check if it's time to export (every 5 minutes at :00, :05, :10, etc.)
                self.check_and_export(current_time)
                
                # Update GUI in main thread
                self.left_gui.root.after(0, self._update_gui)
                
                # Wait for 1 second
                time.sleep(1)
                
            except Exception as e:
                print(f"Error in update loop: {e}")
    
    def check_and_export(self, current_time):
        """Check if it's time to export data (every 5 minutes)"""
        try:
            # Check if we're at a 5-minute interval (00, 05, 10, 15, etc.)
            if current_time.minute % 5 == 0 and current_time.second == 0:
                # Ensure we don't export multiple times for the same minute
                if (self.last_export_time is None or 
                    current_time.minute != self.last_export_time.minute):
                    
                    self.last_export_time = current_time
                    
                    # Schedule export in main thread to avoid GUI conflicts
                    self.left_gui.root.after(0, self._perform_export)
                    
        except Exception as e:
            print(f"Error checking export time: {e}")
    
    def _perform_export(self):
        """Perform the actual export"""
        try:
            success = self.excel_exporter.export_data()
            if success:
                print(f"Excel export completed at {datetime.now().strftime('%H:%M:%S')}")
            else:
                print(f"Excel export failed at {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"Error during export: {e}")
                
    def _update_gui(self):
        """Update GUI elements"""
        try:
            # Refresh the graph for currently displayed appliance
            self.left_gui.refresh_current_graph()
            
            # Update properties display for current appliance
            if hasattr(self.left_gui, 'current_appliance') and self.left_gui.current_appliance:
                self.left_gui.update_appliance_display(self.left_gui.current_appliance)
            
            # Update settings display if visible
            self.update_settings_display()
                
        except Exception as e:
            print(f"Error updating GUI: {e}")

    def update_settings_display(self):
        """Update settings interface if currently visible"""
        if hasattr(self.right_gui, 'refresh_settings_if_visible'):
            self.right_gui.refresh_settings_if_visible()
            


