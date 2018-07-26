#!/usr/bin/env python
"""
Created on Thu Dec 21 2017

@author: alisina (Sina Booeshaghi)
---
The class file for connecting and controlling the stepper motors
via grbl firmware and G-Code commands. 
"""

import serial
import time
import glob
import sys

class CannotConnectException(Exception):
	pass


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


class stepper(object):
	"""The class that directly interfaces with the arduino and sends g-code to it.

	This class has the ability to communicate with the serial port on your computer
	(the case of a mac, the arduino is plugged into my left USB port and the port is named
	/dev/cu.usbmodem1411, the right one is /dev/cu.usbmodem1421
	"""

	####################################################
	#	Initialize/Establish connection with the board
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

		self.port_nano = '/dev/cu.usbserial-A9M11B77'
		self.port_uno = "/dev/cu.usbmodem1411"
		self.baudrate = baudrate
		try:
			print("Attempting to connect to board..")
			self.serial = serial.Serial()
			self.serial.port = self.port_uno
			self.serial.baudrate = 115200
			self.serial.parity = serial.PARITY_NONE
			self.serial.stopbits = serial.STOPBITS_ONE
			self.serial.bytesize = serial.EIGHTBITS
			self.serial.timeout = 1

			self.serial.open()
		except:
			print("Cannot connect to board.")
			raise CannotConnectException
			

		# Now initialize the steppers
		self.axes = ['X', 'Y', 'Z']
		self.direction = ['+', '-']
		self.units = 'G21' # metric (mm) units. if you want to use inches (not recommended) then put G20
		self.maxSpeed = 400.000 # mm/sec # max speed mm/min = *1/60 mm/sec
		self.accel = 50.000 # mm/sec^2
		self.numSteps = 200 # predetermined by the type of motor, num of steps per revolution
		self.microstepping = 32 # num of microsteps per step
		self.shaftDiameter = 5 # mm
		self.shaftPitch = 0.8 # mm
		self.distancePerStep = self.shaftPitch/self.numSteps/self.microstepping #mm/step

		self.conversionFactorStep = 1/self.distancePerStep # steps per mm

		# # Wake up grbl
		self.serial.write("\r\n\r\n".encode())
		# print "this is written"
		time.sleep(2)   # Wait for grbl to initialize 
		self.serial.flushInput()  # Flush startup text in serial input
		# print 'These lines are good'

		# # Stream g-code to grbl
		with open('init.gcode', 'r') as f:
			for i in range(20):
				next(f)
			for line in f:
				# print line
				l = line.partition(';')[0] # Strip all EOL characters for consistency
				print('Writing: ' + l)
				# print 'Sending: ' + l,
				to_write = l + '\n'
				self.serial.write(to_write.encode()) # Send g-code block to grbl
				grbl_out = self.serial.readline() # Wait for grbl response with carriage return
				#print(str(" : " + grbl_out.strip()))
		#print("Connection successful!")



	# These are stepper methods

	def initialize(self):
		# # Wake up grbl
		self.serial.write("\r\n\r\n".encode())
		# print "this is written"
		time.sleep(2)   # Wait for grbl to initialize 
		self.serial.flushInput()  # Flush startup text in serial input
		# print 'These lines are good'

		# # Stream g-code to grbl
		with open('init.gcode', 'r') as f:
			for i in range(20):
				next(f)
			for line in f:
				# print line
				l = line.partition(';')[0] # Strip all EOL characters for consistency
				print('Writing: ' + l)
				# print 'Sending: ' + l,
				to_write = l + '\n'
				self.serial.write(to_write.encode()) # Send g-code block to grbl
				grbl_out = self.serial.readline() # Wait for grbl response with carriage return
				
				#print(str(" : " + grbl_out.strip()))

	def pause(self):
		"""Pauses motion of stepper motor. This command is executed immediately upon being sent to the board.

			Args:
				None
			Returns:
				None
			Raises:
				None"""
		self.serial.write("!".encode())

	def resume(self):
		"""Resumes motion of stepper motor. This command is executed immediately upon being sent to the board. 
			If executed after being paused, it picks up where the previous command left off.

			Args:
				None
			Returns:
				None
			Raises:
				None"""
		self.serial.write("~".encode())

	def reset(self):
		"""Immediately halts and safely resets steppers without power cycle. If steppers in motion, position
			may be lost, and need to re-zero. If steppers not in motion, then position is retained.

			Args:
				None
			Returns:
				None
			Raises:
				None"""
		# self.pause()
		# timer.sleep(3)
		# Time to explain this weird thing. So "\030" is the way of writing Cntrl-x in the octal numeric 
		# system. And it works, so I am not complaining. It stops the controller and flushes the buffer.
		self.serial.write("\030".encode())
		self.initialize()
		# since this resets grbl, I need to call init to resend all of those commands. 
		# TODO: write init as a function and call it after class.

	def close(self):
		"""Closes the port between the computer and the board. This is done after the system has been used 
			to allow other devices to have access to the port.

			Args:
				None
			Returns:
				None
			Raises:
				None"""
		self.serial.close()

	def check_ports(self):
		#serial.tools.list_ports
		return

	def test(self):
		#self.jog(0, 1, 50, 10)
		#self.jog(1, 1, 50, 10)
		self.jog(2, 1, 50, 10)
		#grbl_out = self.serial.readline()
		#print ' : ' + grbl_out.strip()

		#print 'X axis testing complete.\n'

		# time.sleep(3)

		# self.jog(1, 1, 100, 10)
		# # grbl_out = self.serial.readline()
		# # print ' : ' + grbl_out.strip()
		# print 'Y axis testing complete.\n'
		# time.sleep(3)

		# self.jog(2, 1, 100, 10)
		# grbl_out = self.serial.readline()
		# print ' : ' + grbl_out.strip()
		# print 'Z axis testing complete.\n'



	def jog(self, axis, direction, distance, speed):
		"""Attempts to connect to the arduino so that we can talk to it.

			Args:
				axis (int = 0, 1, 2): the axis that we wish to move. In this representaiton, the 0 
				corresponds to the 'x-axis' the 1 to the 'y-axis', and the 2 to the 'z-axis'.

				direction (int = 0 or 1): tells us to move forward (0) or backward (1).

				distance (float): the distance (in mm) that we wish to travel with the given motor.

				speed (float): the speed (in mm/sec)
			Returns:
				None
			Raises:
				None"""
		self.serial.flushInput()
		speed = speed*60 # converts to mm/min since this is what Gcode takes in
		chosenAxis = str(self.axes[axis])
		chosenDirection = str(self.direction[direction])

		command = 'G91 ' + 'G01 ' + chosenAxis + chosenDirection + str(distance)# \+ ' F' + str(speed) + '\n'
		print(command)
		self.serial.write(command.encode())

	def dispense(self, axis, syringeVolume, desiredAmount, desiredFlowRate):
		"""Allows for sending G-code to the stepper which is determined by Syringe Volume and
		amount of fluid that the user wants to dispense per hour. This will only work with BD
		plastic syringes, since the size of the syringe dictates the flow rate

		Thoughts: these values will be G-Code.

			Args: 
				syringeVolume (int): one of the sizes available for BD syringes. The type of syringe
				tells us how linear motion of the plunger is related to volume dispensed. The options
				are listed below:

				Syringe Volume (mL)	|		Syringe Area (mm^2)
				-----------------------------------------------
					1				|			17.34206347
					3				|			57.88559215
					5				|			112.9089185
					10				|			163.539454
					20				|			285.022957
					30				|			366.0961536
					60				|			554.0462538

				IMPORTANT: These are for BD Plastic syringes ONLY!! Others will vary.

				desiredFlowRate (float): the amoung of fluid that the user wants to dispense. For
				our purposes I will operate in [mL/hour].
			Returns:
				None
			Raises:
				None
		"""
		 #TODO: given a syringe am mL amount to dispence, travel that amount.

		 # We can index syringes volume 1-60mL [0-6] respectively
		self.syringeVolumes = [1, 3, 5, 10, 20, 30, 60]
		self.syringeAreas = [17.34206347, 57.88559215, 112.9089185, 163.539454, 285.022957, 366.0961536, 554.0462538]
		try:
			 syringeIndex = self.syringeVolumes.index(syringeVolume)
			 syringeArea = self.syringeAreas[syringeIndex]
		except ValueError:
			print("You did not select a type of syringe that is available.")

		 # Goal: we want to write (to the motor) the rotational (or the linear) speed given the 
		 # threaded rod pitch and the rotations per sec.

		 # now motor speed is in mm/min
		 # flow rate [mL/hr] = mm^2 * mm/min*60min/1hr * 10^-3
		setMotorSpeed = desiredFlowRate*syringeArea/10**3/60

		 # need to determine amout dispensed
		 # amount is in mL and we want to convert this to mm of travel for the motor
		setMotorDistance = desiredAmount*10**3/syringeArea

		direction = 0

		self.jog(axis, direction, setMotorDistance, setMotorSpeed)

try:
	stp = stepper()
	time.sleep(5)
	stp.test()
	pass
except CannotConnectException:
	print("Could not connect to board try again")


# # Open grbl serial port
# s = serial.Serial('/dev/cu.usbmodem1411',115200)

# # Open g-code file
# f = open('grbl.gcode','r');

# # Wake up grbl
# s.write("\r\n\r\n")
# time.sleep(2)   # Wait for grbl to initialize 
# s.flushInput()  # Flush startup text in serial input

# # Stream g-code to grbl
# for line in f:
#     l = line.strip() # Strip all EOL characters for consistency
#     print 'Sending: ' + l,
#     s.write(l + '\n') # Send g-code block to grbl
#     grbl_out = s.readline() # Wait for grbl response with carriage return
#     print ' : ' + grbl_out.strip()

# # Wait here until grbl is finished to close serial port and file.
# raw_input("  Press <Enter> to exit and disable grbl.") 

# # Close file and serial port
# f.close()
# s.close()


