from communication import LoRaCommunication
import scheduler
import deviceData

from SX127x.LoRa import *
from SX127x.board_config import BOARD
from SX127x.LoRaArgumentParser import LoRaArgumentParser

import time

def main():
    lora = LoRaCommunication(verbose=False)
    lora.set_mode(MODE.STDBY)
    lora.set_pa_config(pa_select=1)
    lora.set_spreading_factor(7)
    lora.set_bw(7)
    lora.set_coding_rate(CODING_RATE.CR4_5)
    lora.set_rx_crc(True)
    lora.set_freq(915.0)

    try:
        lora.set_mode(MODE.RXCONT)
        print("LoRa Receiver Mode")

        while True:
            user_input = input("blah blah blah")
            if user_input:
                lora.send_message(user_input)
            else:
                print("Listening for incoming messages....")
                time.sleep(1)
                if lora.device_data:
                    print(f"Current Device Data: {lora.device_data}")
    except KeyboardInterrupt:
        print("Exiting program")
    finally:
        lora.set_mode(MODE.SLEEP)
        BOARD.teardown()


if __name__ == '__main__':
    main()


