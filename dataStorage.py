import pandas as pd

def applianceSetup(appliances, powerLimits, currentLimits, voltageLimits, instantCurrent, instantVoltage, instantPower, averageCurrent, averageVoltage, dutyCycle, operationTime):

    data = {
        'power limit [W]': powerLimits,
        'current limit [A]': currentLimits,
        'voltage limit [V]': voltageLimits,
        'instantaneous current [A]': instantCurrent,
        'instantaneous voltage [V]': instantVoltage,
        'instantaneous power [W]': instantPower,
        'average current [A]': averageCurrent,
        'average voltage [V]': averageVoltage,
        'duty cycle [%]': dutyCycle,
        'time in operation [s]': operationTime 
    }

    df = pd.DataFrame(data, index=appliances)

    return df

def updateApplianceData(df, applianceName, columnName, newvalue):

    if applianceName in df.index and columnName in df.columns:
        df.at[applianceName, columnName] = newvalue
        print(f"updates appliance '{applianceName}', column '{columnName}' with new value: {newvalue}")
    else:
        print("Invalid appliance name or column name")


