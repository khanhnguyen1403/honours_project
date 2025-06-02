import time
import tkinter as tk
from loraFunctionality import loraSetup, sendAT, receive, echo, testConnection, testConnectivity
from dataStorage import applianceSetup, updateApplianceData
from graphicalUserInterface import App
import threading

def listener(app, df, appliance_name):
    message = receive()

    # Process the received message
    try:
        # Extract values from the message
        parts = message.split(',')
        power = float(parts[0].split(': ')[1].replace(' V', '').strip())
        voltage = float(parts[1].split(': ')[1].replace(' V', '').strip())
        current = float(parts[2].split(': ')[1].replace(' A', '').strip())
                
        # # Update the GUI with the received values
        # app.root.after(0, app.update_power_voltage_current, power, voltage, current)

        # Update the backend data
        updateApplianceData(df, appliance_name, 'instantaneous voltage [V]', voltage1)
        updateApplianceData(df, appliance_name, 'instantaneous voltage [V]', voltage2)
        updateApplianceData(df, appliance_name, 'instantaneous current [A]', current)

        # Fetch updated data from the backend and update the GUI
        app.root.after(0, app.update_from_backend, df, appliance_name)

    except (ValueError, IndexError) as e:
            app.root.after(0, app.systemMessages, f"Error: Invalid data format received. {str(e)}")

    time.sleep(0.1)

    app.root.after(0, app.systemMessages, message)

def main():
    print("Central Control Node Startup")


    print("-------------------------------------")
    print("       ESTABLISH DATA STORAGE        ")
    print("-------------------------------------")

    appliances = ['appliance1']
    powerLimits = [1000]
    currentLimits = [10]
    voltageLimits = [50]
    instantCurrent = [5.0]
    instantVoltage = [49.7]
    instantPower = [(instantCurrent[0]*instantVoltage[0])]
    averageCurrent = [4.8]
    averageVoltage = [50]
    dutyCycle = [80]
    operationTime = [10]

    df = applianceSetup(appliances, powerLimits, currentLimits, voltageLimits, instantCurrent, instantVoltage, instantPower, 
                        averageCurrent, averageVoltage, dutyCycle, operationTime)
    
    print(df)

    print("-------------------------------------")
    print("     ESTABLISH LORA CONNECTION       ")
    print("-------------------------------------")
    
    loraSetup()
    #test for local LoRa connection
    testStatus = testConnection()
    if testStatus == True:
        print('local LoRa radio is ready\n')
    else:
        print('No local LoRa-E5 detected\n')
        exit()

    #Test for load side LoRa    
    # testStatusPair = False
    # while testStatusPair == False:
    #     testStatusPair = testConnectivity()
    #     if testStatusPair == True:
    #         print('Pair LoRa radio is ready\n')
    #         break
    #     else:
    #         print('No pair LoRa-E5 detected. Waiting...\n')
    #         time.sleep(2)

    print("-------------------------------------")
    print("           INITIALISE GUI            ")
    print("-------------------------------------")

    root = tk.Tk()
    app = App(root)

    listener_thread = threading.Thread(target=listener, args=(app,df,'appliance1'), daemon=True)
    listener_thread.start()

    root.mainloop()


if __name__=="__main__":
    main()