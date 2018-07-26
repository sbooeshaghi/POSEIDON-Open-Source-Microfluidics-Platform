import serial
import time
import glob
import sys
import struct
import time

print(struct.pack('>B', 0))

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

port = serial_ports()[-1]

class CannotConnectException(Exception):
    pass

class arduino(object):
    """The class that directly interfaces with the arduino and sends commands to it.

    This class has the ability to communicate with the serial port on your computer
    (the case of a mac, the arduino is plugged into my left USB port and the port is named
    /dev/cu.usbmodem1411, the right one is /dev/cu.usbmodem1421
    """

    ####################################################
    #   Initialize/Establish connection with the board
    ####################################################

    def __init__(self, port='', baudrate=115200):
        """Attempts to connect to the arduino so that we can talk to it.

            Args:
                port (string): the specific port that your aduino is connected to. By going to 
                the arduino IDE you can click on Tools/Port and the dropdown menu should tell you
                where your arduino is connected to. (should be COM3 on Windows, /dev/ttyUSB0 on GNI/Linuz)

                baudrate (int): this is a number that tells us the number of signal changes per second.
                So it in essence is a descriptor for how many times per second information is 
                transferred to and from the arduino. 
            Returns:
                None
            Raises:
                None
        """

        #self.port_nano = '/dev/cu.usbserial-A9M11B77'
        #self.port_uno = "/dev/cu.usbmodem1411"
        self.baudrate = baudrate
        try:
            print("Attempting to connect to board..")
            self.serial = serial.Serial()
            self.serial.port = port
            self.serial.baudrate = 115200
            # self.serial.parity = serial.PARITY_NONE
            # self.serial.stopbits = serial.STOPBITS_ONE
            # self.serial.bytesize = serial.EIGHTBITS
            #self.serial.timeout = 1
            self.serial.setDTR = False
            self.serial.setRTS = False

            self.serial.open()
            print("Connected to board!\n")
        except:
            print("Cannot connect to board.")
            raise CannotConnectException

    def close(self):
        self.serial.close()

###############################
# Sending and receiving strings to and from the arduino is done in the following way: 
# In [41]: s = b'blah'
# In [42]: type(s)
# Out[42]: bytes

# In [43]: s = s.decode('utf-8')
# In [44]: type(s)
# Out[44]: str

# Sending and receiving numbers to and from the arduino is done in the following way:
# In [46]: n = 100
# In [47]: n = (n).to_bytes(2, byteorder="big")
# In [48]: n
# Out[48]: b'\x00d'

# In [49]: int.from_bytes(n, byteorder="big")
# Out[49]: 100
###############################


ard = arduino(port=port)
print("Serial port you are connecting to: ", ard.serial.name)

time.sleep(2)
print("Is the serial port open?", ard.serial.isOpen(), "\n")

string2send = "1435" + "\n"
num = 123.123
#num2send = struct.pack('f', num)
#print("Sending message: ", num2send)
ard.serial.write(b"<LED1, 200, 0.5>")
line = []
try:
    if ard.serial.isOpen():
        while True:
            data = ard.serial.read()
            print(struct.unpack('f', data))
    print("not open")
except KeyboardInterrupt:

    ard.close()
    print("You closed the connection")