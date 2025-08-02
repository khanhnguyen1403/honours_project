from appliance import Appliance
from uppergui import Upper_GUI
from left_gui import Left_GUI
from right_gui import Right_GUI
from root_gui import RootGUI


if __name__ == "__main__":
    appliances = {
        "All":None,
        "Washing Machine": Appliance("Washing Machine", 1),
        "Air Conditioner": Appliance("Air Conditioner", 2),
        "Heater": Appliance("Heater", 3)
    }
    
    # Initialising GUI components
    root_gui = RootGUI()
    upper_gui = Upper_GUI(root_gui.root, None, appliances) 
    right_gui = Right_GUI(root_gui.root, upper_gui)
    upper_gui.right_gui = right_gui
    left_gui = Left_GUI(root_gui.root, [0, 1, 2, 3, 4, 5])
    upper_gui.left_gui = left_gui

    #Initialising GUI notification
    right_gui.log_events("GUI initialized")

    root_gui.root.mainloop()
