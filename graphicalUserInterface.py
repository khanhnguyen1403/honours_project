import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from datetime import datetime
# from loraFunctionality import sendAT

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("DC Nanogrid Central Control Node")
        self.root.geometry("800x480")

        # Initialize pwmCommand variable
        self.pwmCommand = None

        # Set theme to dark
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Create the notebook widget (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill=tk.BOTH)

        # Page 1 - User Input for Appliance Selection
        self.page1 = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.page1, text="Appliance Request")

        # Appliance Dropdown (now touch-friendly)
        self.appliance_label = ctk.CTkLabel(self.page1, text="Select Appliance:")
        self.appliance_label.pack(pady=5)

        self.appliance_options = ["Washing Machine", "Dishwasher", "Fan", "Air Conditioner"]
        self.appliance_dropdown = ctk.CTkOptionMenu(self.page1, values=self.appliance_options)
        self.appliance_dropdown.pack(pady=5)
        self.appliance_dropdown.set(self.appliance_options[0])  # default

        # Operation Time Input
        self.time_label = ctk.CTkLabel(self.page1, text="Operation Time (hours):")
        self.time_label.pack(pady=5)

        self.time_entry = ctk.CTkEntry(self.page1)
        self.time_entry.pack(pady=5)

        # Deadline Input
        self.deadline_label = ctk.CTkLabel(self.page1, text="Deadline (YYYY-MM-DD HH:MM):")
        self.deadline_label.pack(pady=5)

        self.deadline_entry = ctk.CTkEntry(self.page1)
        self.deadline_entry.pack(pady=5)

        # PWM Command Input (using a touch-friendly slider)
        self.pwm_label = ctk.CTkLabel(self.page1, text="PWM Command (0-100):")
        self.pwm_label.pack(pady=5)

        self.pwm_slider = ctk.CTkSlider(self.page1, from_=0, to=100)
        self.pwm_slider.pack(pady=5)

        # Submit Button
        self.submit_button = ctk.CTkButton(self.page1, text="Submit", command=self.submit)
        self.submit_button.pack(pady=10)

        # Page 2 - Placeholder for Nanogrid Data (Example)
        self.page2 = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.page2, text="Nanogrid Data")
        
        # Power Consumption Labels
        self.power_label = ctk.CTkLabel(self.page2, text="Power (W):")
        self.power_label.pack(pady=15)
        
        self.voltage_label = ctk.CTkLabel(self.page2, text="Voltage (V):")
        self.voltage_label.pack(pady=15)
        
        self.current_label = ctk.CTkLabel(self.page2, text="Current (A):")
        self.current_label.pack(pady=15)

        # Page 3 - System Messages and Errors
        self.page3 = ctk.CTkFrame(self.notebook)
        self.notebook.add(self.page3, text="System Messages")

        self.log_box = ctk.CTkTextbox(self.page3, height=300, width=500)
        self.log_box.pack(pady=20)

        # Example message for log
        self.log_box.insert(tk.END, "System initialized successfully.\n")

    def submit(self):
        # Read PWM Command from the slider value when submitting
        self.pwmCommand = int(self.pwm_slider.get())
        
        try:
            if 0 <= self.pwmCommand <= 100:
                # Log the PWM command
                self.log_box.insert(tk.END, f"Submitting PWM Command: {self.pwmCommand}%\n")
                self.log_box.yview(tk.END)
                
                # Send the PWM command over LoRa
                self.send_pwm_over_lora(self.pwmCommand)
            else:
                raise ValueError("PWM Command must be an integer between 0 and 100")

        except ValueError as e:
            self.log_box.insert(tk.END, f"Error: {str(e)}\n")
            self.log_box.yview(tk.END)

    def send_pwm_over_lora(self, pwmCommand):
        print(f"Sending PWM Command: {pwmCommand}% over LoRa")
        pwm = str(pwmCommand)
        sendAT(pwm)

    def update_power_voltage_current(self, power, voltage, current):
        # Update the power, voltage, and current labels in the GUI
        self.power_label.config(text=f"Power: {power:.2f} kWh")
        self.voltage_label.config(text=f"Voltage: {voltage:.2f} V")
        self.current_label.config(text=f"Current: {current:.2f} A")
    
    def systemMessages(self, message):
        messageDisp = str(message)
        self.log_box.insert(tk.END, f" {message}\n")
        self.log_box.yview(tk.END)

    def update_from_backend(self, df, appliance_name):
            # Fetch updated values from the DataFrame and update the labels
            power = df.at[appliance_name, 'instantaneous power [V]']  # Get voltage1
            voltage = df.at[appliance_name, 'instantaneous voltage [V]']  # Get voltage2
            current = df.at[appliance_name, 'instantaneous current [A]']  # Get current

            self.power_label.config(text=f"Power (W): \n{power:.2f} W")
            self.voltage_label.config(text=f"Voltage (V): \n{voltage:.2f} V")
            self.current_label.config(text=f"Current (A): \n{current:.2f} A")


# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
