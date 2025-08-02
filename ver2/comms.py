import serial
from time import sleep

ser = serial.Serial('/dev/tty.usbserial-1410', 9600)

def send_at_command(command):
    message = ('AT' + command + '\r\n').encode('utf-8')
    ser.write(message)

# Setup
send_at_command("+MODE=TEST")
send_at_command("+TEST=?")
send_at_command("+TEST=RFCFG,920,SF7,500,12,12,14,ON,OFF,OFF")

print("Waiting for data...")

data_buffer = {}

while True:
    send_at_command("+TEST=RXLRPKT")
    line = ser.readline().decode('utf-8').strip()

    if line.startswith('+TEST: RX '):
        print("Raw data:", line)
        try:
            start = line.find('"') + 1
            end = line.rfind('"')
            hex_str = line[start:end]
            ascii_str = bytes.fromhex(hex_str).decode('ascii').strip()
            print("ASCII data:", ascii_str)

            # Expecting format like V0:3.30, I0:1.50, P0:4.95
            if ':' in ascii_str:
                label_with_id, val_str = ascii_str.split(':', 1)
                label = label_with_id[0]  # V, I, or P
                cycle_id = label_with_id[1:]  # e.g., "0"
                val = float(val_str)

                if cycle_id not in data_buffer:
                    data_buffer[cycle_id] = {}

                data_buffer[cycle_id][label] = val

                if all(k in data_buffer[cycle_id] for k in ['V', 'I', 'P']):
                    v = data_buffer[cycle_id]['V']
                    i = data_buffer[cycle_id]['I']
                    p = data_buffer[cycle_id]['P']
                    print(f"[Cycle {cycle_id}] Voltage: {v} V, Current: {i} A, Power: {p} W\n")

                    del data_buffer[cycle_id]  # Clear completed cycle

        except Exception as e:
            print("Error parsing:", e)

    sleep(1)