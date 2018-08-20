import serial
import time
import glob
import sys

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

ser = serial.Serial() # ttyACM1 for Arduino board
ser.port = port
ser.baudrate = 115200
ser.timeout = 1
ser.setDTR = False
ser.setRTS = False
ser.close()
ser.open()

readOut = 0   #chars waiting from laser range finder

print ("Starting up")
connected = False
commandToSend = 1 # get the distance in mm

while True:
    print ("Writing: ",  commandToSend)
    ser.write(str(commandToSend).encode())
    time.sleep(1)
    while True:
        try:
            print ("Attempt to Read")
            readOut = ser.readline().decode('ascii')
            time.sleep(1)
            print ("Reading: ", readOut) 
            break
        except:
            pass
    print ("Restart")
    ser.flush() #flush the buffer