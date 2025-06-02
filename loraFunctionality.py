
import serial
import time

loRa = serial.Serial ("/dev/tty.usbserial-1410", 9600)    #Open port with baud rate
#/dev/ttyUSB0

def loraSetup():

    print('------------Serial UART Connection Set-----------')
    print('GPIO 14 (TX) --> LoRa RX')
    print('GPIO 15 (RX) --> LoRa TX')
    print('baudrate = 9600')
    print('Raspberry Pi 5 Serial port - /dev/ttyAMA0')
    print('-------------------------------------------------')

    time.sleep(1)

    # Region specific setup
    print('Configuring Regional Settings...')
    band='AU915' #set the band
    channels='8-15' #enable channels 8-15
    DR='0' #set RF modulation to SF12/125 i.e. 125kHz i.e. 250 bits/s

    sendAT('+DR=' + band)
    sendAT('+DR=' + DR)
    sendAT('+CH=NUM,' + channels)
    sendAT('+MODE=LWOTAA') #set mode to LoRaWAN Over-The-Air-Activation
    receive() # flush

    print('done.\n')
    print('-----------------------')
    print('Check DR:\n')
    sendAT('+DR') #check current selected data rate
    data = receive()
    print(data)
    print('-----------------------')

def receive():
    '''Polls the uart until all data is dequeued'''
    rxData=bytes()
    while loRa.in_waiting>0:
        rxData += loRa.read(1)
        time.sleep(0.002)
    return rxData.decode('utf-8')

def testConnection():
    '''Checks for good UART connection by querying the LoRa-E5 module with a test command'''
    sendAT('') # empty at command will query status
    data = receive()
    print(data)
    if data == '+AT: OK\r\n' : 
        test = True
    else:
        test = False
    return test

def sendAT(command):
    '''Wraps the "command" string with AT+ and \r\n'''
    buffer = 'AT' + command + '\r\n'
    buffer = buffer.encode('utf-8')
    loRa.write(buffer)
    print("sent command over LoRa")
    time.sleep(0.300)

def echo():
    while loRa.in_waiting > 0:
        rxData = loRa.readline()
        print(rxData.decode('utf-8'))

def testConnectivity():
    testPhrase = "hello world"
    testPhraseReply = "hi earth"
    sendAT(testPhrase)
    reply = receive()
    if reply == testPhraseReply:
        testConnectivity = True
    else:
        testConnectivity = False
    return testConnectivity


