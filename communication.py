import time
from deviceData import DeviceData

from SX127x.LoRa import *
from SX127x.board_config import BOARD
from SX127x.LoRaArgumentParser import LoRaArgumentParser

BOARD.setup()
     
class LoRaCommunication(LoRa):
    def __init__(self,device_data, verbose=False):
        super(LoRaCommunication,self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0]*6)
        self.device_data = device_data

    def on_rx_done(self):
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        message = bytes(payload).decode("utf-8", 'ignore')
        print(f"received message: {message}")

        try:
            device_name,voltage,current = message.split(',')
            voltage = float(voltage)
            current = float(current)
            if self.device_data is None:
                self.device_data = DeviceData(device_name, voltage, current)
            else:
                self.device_data.update_data(voltage, current)

            print(f"Updates {self.device_data.device_name}: Voltage={voltage} V, Current={current} A")
        except ValueError:
            print("Invalid data format received.")

        self.reset_ptr_rx()
        self.set_mode(MODE.RXCONT)

    def sendMessage(self, message):
        self.set_mode(MODE.STDBY)
        self.clear_irq_flags(TxDone=1)
        self.write_payload([ord(char) for char in message])
        self.set_mode(MODE.TX)
        print(f"Sent message: {message}")
        while not self.get_irq_flags()['tx_done']:
            time.sleep(0.1)
        self.set_mode(MODE.RXCONT)   
