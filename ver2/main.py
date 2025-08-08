from appliance import Appliance, Appliance_Summary
from randomvaluegenerator import RandomValueGenerator
from dataupdatemanager import DataUpdateManager
from upper_gui import Upper_GUI
from left_gui import Left_GUI
from right_gui import Right_GUI
from root_gui import RootGUI

if __name__ == "__main__":
    # Create individual appliances
    washing_machine = Appliance("Washing Machine", 1)
    washing_machine.power_rating = 500
    washing_machine.voltage_rating = 250
    washing_machine.type = 0  # Load
    
    air_conditioner = Appliance("Air Conditioner", 2)
    air_conditioner.power_rating = 1200
    air_conditioner.voltage_rating = 200
    air_conditioner.type = 0  # Load
    
    heater = Appliance("Heater", 3)
    heater.power_rating = 800
    heater.voltage_rating = 150
    heater.type = 0  # Load
    
    # Create summary appliance
    appliance_summary = Appliance_Summary("All", 0)
    
    appliances = {
        "All": appliance_summary,
        "Washing Machine": washing_machine,
        "Air Conditioner": air_conditioner,
        "Heater": heater
    }
    
    # Create random value generator and set variation percentages
    value_generator = RandomValueGenerator()
    value_generator.set_appliance_variation("Washing Machine", 5)  # 5% variation
    value_generator.set_appliance_variation("Air Conditioner", 5)  # 5% variation
    value_generator.set_appliance_variation("Heater", 1)  # 1% variation

    # Initialize summary with current appliance data
    appliance_summary.update_from_appliances(appliances)
    
    # Initialising GUI components
    root_gui = RootGUI()
    upper_gui = Upper_GUI(root_gui.root, None, appliances) 
    right_gui = Right_GUI(root_gui.root, upper_gui)
    upper_gui.right_gui = right_gui
    left_gui = Left_GUI(root_gui.root, 0)
    upper_gui.left_gui = left_gui

    # Create and start data update manager
    data_manager = DataUpdateManager(appliances, value_generator, left_gui, right_gui)
    data_manager.start_updates()

    # Initialize with first appliance selected
    initial_appliance = upper_gui.get_current_appliance()
    left_gui.update_appliance_display(initial_appliance)
    left_gui.update_graph(initial_appliance)

    #Initialising GUI notification
    right_gui.log_events("GUI initialized")

    root_gui.root.mainloop()
    
    # Stop data updates when GUI closes
    data_manager.stop_updates()