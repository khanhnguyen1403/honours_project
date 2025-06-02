from machine import Pin, PWM, UART, ADC
from time import sleep
from utime import sleep_ms

#Initialise PWM
pwm = PWM(Pin(29, Pin.OUT))
pwm.freq(1000)

# Set up ADC on GPIO pins for voltage and current measurements
voltage_pin = ADC(Pin(26))  # GPIO 26 as ADC input for voltage
current_pin = ADC(Pin(28))  # GPIO 28 as ADC input for current

SCALING_FACTOR = 3.3 / 65535  # Converts ADC reading to actual values

uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))

duty_value = int(50 * 65535 / 100)  # Scale 0-100 to 0-65535
pwm.duty_u16(duty_value)

sleep(1)

# Function to send command and read response
def send_at_command(command):
    # Convert the command to bytes and send it
    message = ('AT' + command + '\n').encode('utf-8')
    uart.write(message)
    uart.flush()
    print("Sent command:", command)
        
def set_pwm_duty(dutyPercent):
    if 0 <= dutyPercent <= 100:
        duty_value = int(dutyPercent * 65535 / 100)  # Scale 0-100 to 0-65535
        pwm.duty_u16(duty_value)
        print(f"PWM duty cycle set to: {dutyPercent}%")
    else:
        print("Received invalid duty cycle value. Must be between 0 and 100.")
        
def read_sensor_data():
    """ Reads voltage and current from ADC pins and returns the values in volts and amps. """
    # Read raw ADC values
    raw_voltage = voltage_pin.read_u16()
    raw_current = current_pin.read_u16()
    
    # Convert raw values to actual voltage and current
    voltage = raw_voltage * SCALING_FACTOR
    current = raw_current * SCALING_FACTOR
    
    return voltage, current

def send_sensor_data(power, voltage, current):
    data_str = f'{voltage:.2f} {current:.2f} {power:.2f}'
    
    send_at_command(f'+TEST=TXLRSTR, {data_str}')
    
#Initialisation
    
set_pwm_duty(100)

send_at_command("+MODE=TEST")
send_at_command("+TEST=?")
send_at_command("+TEST=RFCFG,915,SF7,500,12,12,14,ON,OFF,OFF")

print("\n")



# Main loop
while True:
#     send_at_command("+TEST=RXLRPKT")
#     rxData=bytes()
#     if uart.any():
#         rxData = uart.read()
#         data = rxData.decode('utf-8').strip()
#         print(f"data: {data}")
    
#     sleep(0.05)  # Delay 
    
    # Read and send sensor data over UART
    voltage, current = read_sensor_data()
    power = voltage * current
    
    send_sensor_data(power, voltage, current)
    print("\n")

    # Small delay for stability
    sleep(1)