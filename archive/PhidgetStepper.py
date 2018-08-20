# -*- coding: utf-8 -*-
"""
"""

# Phidget specific imports
from Phidget22.Devices.Stepper import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from Phidget22.Net import *
# import time module
from time import sleep, time
import sys

#In class definition, any method which has a number argument passed to it
#is most likely the motor index. Eg self.setPosition(0, position) denotes the 0tth motor

class PhidgetStepper(object):
    r"""The main UI class for the PhidgetStepper1067 interface.
    
    This class contains the ability to communicate wiht the interface and read card data for reference.
    """
    ########################################################################
    #        Initialize/Establish connection with the board                #
    ########################################################################
    def __init__(self):
        r""" The initialization of the card. 
        
        Tries to communicate to the board and returns an error if the card fails to establish.
        """
        
        self.errorvalue = False
        try:
            self.Stepper = Stepper()
            
        except RuntimeError as e:
            print("Runtime Exception: %s" % e.details)
            print("Exiting....")
            sys.exit(1)
        try:
            self.Stepper.setOnAttachHandler(StepperAttached)
            self.Stepper.setOnDetachHandler(StepperDetached)
            self.Stepper.setOnErrorHandler(ErrorEvent)

            self.Stepper.setOnPositionChangeHandler(PositionChangeHandler)

            print("Waiting for the Phidget Stepper Object to be attached...")
            self.Stepper.openWaitForAttachment(3000)

        except PhidgetException as e:
            print("Phidget Exception %i: %s" % (e.code, e.details))
            print("Press Enter to Exit...\n")
            readin = sys.stdin.read(1)
            sys.exit(1)

            

            
    ########################################################################
    #        DISPLAY: displays important information about the steppers    #
    ########################################################################
    # def displayDeviceInfo(self):
    #     r""" Displays card data. 
        
    #     If card is succesfully initialized, the data on the card is dsiplayed in the terminal.
    #     """
    #     print("|------------|----------------------------------|--------------|------------|")
    #     print("|- Attached -|-              Type              -|- Serial No. -|-  Version -|")
    #     print("|------------|----------------------------------|--------------|------------|")
    #     print("|- %8s -|- %30s -|- %10d -|- %8d -|" % (self.Stepper.isAttached(), self.Stepper.getDeviceName(), self.Stepper.getSerialNum(), self.Stepper.getDeviceVersion()))
    #     print("|------------|----------------------------------|--------------|------------|")
    #     print("Number of Motors: %i" % (self.Stepper.getMotorCount()))
        
        
    ########################################################################
    #        SETUP: sets up the velocity and acceleration limits           #
    ########################################################################
    def stepperSetup(self, Velocity_limit_mm, Acceleration_limit_mm, Current_limit):
        """
        Set up the input parameters of the Stepper Motor.
        
        Selection of the velocity, acceleration, and current limits for the stepper.
            Args:
                Velocity_limit_mm (float): The maximum velocity of the sled in mm/sec. Optimal setting is ~15-20 mm/sec.
                Acceleration_limit_mm (float): The maximum acceleration of the sled in mm/sec^2. Optimal setting is ~50-70 mm/sec^2.
                Current_limit (float, [0-4]): The current limit (in Amps) delivered to the motor.                
            Returns:
                None            
            Raises:
                AttributeError: None
        """
        self.setEngaged(False)
        
        #VELOCITY: make sure the velocity input isnt out of bounds
        self.setVelocity(Velocity_limit_mm)
            
        #ACCELERATION: make sure the acceleration isnt out of bounds
        self.setAcceleration(Acceleration_limit_mm)
        #CURRENT: limits the amount of current supplied to the board
        self.setCurrentLimit(Current_limit)
        
        # Initialize the Stepper Position
        current_position = self.getCurrentPosition()
        self.setTargetPosition(current_position)
        self.setEngaged(False)
        
    ########################################################################   
    # GETTERS: Get all values relevant to the motor in form self.getter    #
    ########################################################################
    def getCurrentLimit(self):
        """
        Returns the Current Limit for the stepper motor.
        
            Args:
                None
            Returns:
                currentLimit (float): will be a value [0, 4].
            Raises:
                AttributeError: None
        """
        currentLimit = self.Stepper.getCurrentLimit(0)   
        return currentLimit
    def getVelocityLimit(self):
        """
        Returns the Velocity Limit for the stepper motor, essentially the upper bound for velocity during any operation of the stepper motor. (Not to be confused with self.getVelocity() which returns the current velocity of the motor (0 if not moving))
        
            Args:
                None
            Returns:
                velocityLimit (float): The velocity limit value will be in mm/sec.
            Raises:
                AttributeError: None
        """
        velocityLimit = self.Stepper.getVelocityLimit(0)*self.getConversionFactor()
        return velocityLimit
    def getVelocity(self):
        """
        Returns the current Velocity of the stepper motor. (Not to be confused with self.getVelocityLimit() which returns the upper bound for the velocity of the motor)
        
            Args:
                None
            Returns:
                velocity (float): The current velocity value will be in mm/sec.
            Raises:
                AttributeError: None
        """        
        velocity = self.Stepper.getVelocity(0)*self.getConversionFactor()
        return velocity
    def getAcceleration(self):
        """
        Returns the Acceleration limit of the stepper motor. 
        
            Args:
                None
            Returns:
                acceleration (float): The current acceleraion value will be in mm/sec^2.
            Raises:
                AttributeError: None
        """         
        acceleration = self.Stepper.getAcceleration(0)*self.getConversionFactor()
        return acceleration
    def getCurrentPosition(self):
        """
        Returns the current Position of the stepper motor. 
        
            Args:
                None
            Returns:
                currentPosition (float): The current position value will be in mm. Referenced from the zero value, wherever it is defined to be.
            Raises:
                AttributeError: None
        """           
        currentPosition = self.Stepper.getCurrentPosition(0)*self.getConversionFactor()
        return currentPosition
    def getConversionFactor(self):
        """
        Returns the Conversion Factor for the stepper motor/threaded rod combo. If those two things are changed, conversion factor wil change.
        
            Args:
                None
            Returns:
                conversionFactor (float): The conversion factor value will be in mm/steps.
            Raises:
                AttributeError: None
        """   
        conversionFactor = self.setConversionFactor() 
        return conversionFactor 
        
    ########################################################################
    #    SETTERS: Set all values for motor in form self.setter(value)      #
    ########################################################################
    def setEngaged(self, state): #state is a True or False Boolean
        """
        Sets the state (connectedness) of the stepper motor. 
        
            Args:
                State (bool): True means that the stepper will be engaged, False means it will be disengaged.
            Returns:
                None.
            Raises:
                AttributeError: None
        """   
        self.Stepper.setEngaged(0, state)
    def setConversionFactor(self, factor=2*16*1.016/(1000*200)):
        """
        Sets the Conversion Factor of the stepper motor. This is used to convert the TPI (Threads Per Inch) into mm for many getFunctions.
        
            Args:
                factor (float): The factor needs to be calculated by hand per rig setup, but only needs to be done once. DefaultValue = 2*16*1.016/(1000*200).
            Returns:
                None.
            Raises:
                AttributeError: None
        """           
        return factor
    def setCurrentLimit(self, current):
        """
        Sets the Current Limit for the stepper motor.
        
            Args:
                current (float): Any value is accepted, but if a value is > maxCurrent or < minCurrent, then 0, 4 are set respectively. Unit is in amps.
            Returns:
                None.
            Raises:
                AttributeError: None
        """
        min_current = self.Stepper.getCurrentMin(0)
        max_current = self.Stepper.getCurrentMax(0)

        if current < min_current:
            self.Stepper.setCurrentLimit(0, min_current)
        elif current > max_current:
            self.Stepper.setCurrentLimit(0, max_current)
        else:
            self.Stepper.setCurrentLimit(0, current)
    def setVelocity(self, velocity):
        """
        Sets the Velocity of the stepper motor. During operation, the velocity of the motor, will not exceed this value.
        
            Args:
                velocity (float): Any value is accepted, but if a value is > maxVelocity or < minVelocity, then minVelocity/maxVelocity are set respectively. Units are in mm/sec.
            Returns:
                None.
            Raises:
                AttributeError: None
        """
        velocity_steps = velocity/self.getConversionFactor() #converts from mm/sec -> 1/16th step/sec     
        max_V = self.Stepper.getVelocityMax(0)
        min_V = self.Stepper.getVelocityMin(0)
        
        if velocity_steps > max_V:
            self.Stepper.setVelocityLimit(0,max_V)
        elif velocity_steps < min_V:
            self.Stepper.setVelocityLimit(0,min_V)
        else:
            self.Stepper.setVelocityLimit(0, int(velocity_steps))    
    def setAcceleration(self, acceleration):
        """
        Sets the Acceleration of the stepper motor. During operation, the acceleration of the motor, will not exceed this value.
        
            Args:
                acceleration (float): Any value is accepted, but if a value is > maxAcceleration or < minAcceleration, then minAcceleration/maxAcceleration are set respectively. Units are in mm/sec^2.
            Returns:
                None.
            Raises:
                AttributeError: None
        """        
        acceleration = acceleration/self.getConversionFactor() #converts from mm/sec -> 1/16th step/sec
        max_A = self.Stepper.getAccelerationMax(0)
        min_A = self.Stepper.getAccelerationMin(0)
           
        if acceleration > max_A:
            self.Stepper.setAcceleration(0,max_A)
        elif acceleration < min_A:
            self.Stepper.setAcceleration(0,min_A)
        else:
            self.Stepper.setAcceleration(0, int(acceleration))           
    def setCurrentPosition(self, position):
        """
        Sets the Current Position of the stepper motor. This is used for "zero"ing out the motor position. Should only be called when setEngaged(False)
        
            Args:
                position (float): Any value is accepted, but if position is < minPosition or > maxPosition, set min/max respectively. Motor will know that it is in that new, set, position.
            Returns:
                None.
            Raises:
                AttributeError: None
        """
        self.setEngaged(False)
        position = position/self.getConversionFactor()
        min_position = 0            
        max_position = self.Stepper.getPositionMax(0)
                
        if position < 0:
            self.Stepper.setCurrentPosition(0, min_position)
        elif position > max_position:
            self.Stepper.setCurrentPosition(0, max_position)
        else:
            self.Stepper.setCurrentPosition(0, int(position))
            
        self.setEngaged(True)
    def setTargetPosition(self, targetPosition):
        """
        Sets the Target Podiyion of the stepper motor. One of the main methods in home and jog. By having the current position be different from the target position, the motor will move.
        
            Args:
                targetPosition (float): Any value is accepted, but if a value is > maxVelocity or < minVelocity, then minVelocity/maxVelocity are set respectively. Units are in mm/sec.
            Returns:
                None.
            Raises:
                AttributeError: None
        """
        #Large positive Value will move steppers counterclockwise
        #Large negative value will move steppers clockwise
        #target position is in mm
        targetPosition = targetPosition/self.getConversionFactor()
        self.setEngaged(True)
        self.Stepper.setTargetPosition(0, int(targetPosition))

        
    ########################################################################    
    #                            MOVEMENT FEATURES                         #
    ########################################################################        
        
    def jog(self, mm_interval):
        """
        Jogs the motor a certain distance in a certain direction.

        The motor will jog forward (towards the center) if the mm_interval is positive, and backward (away from center) if the mm_interval is negative.        
            Args:
                mm_interval (float): The distance in mm that you would like to jog the motor.
            Returns:
                None.
            Raises:
                AttributeError: None
        """
        self.setEngaged(True)        
        self.setTargetPosition(self.getCurrentPosition()+mm_interval)
        self.setEngaged(False)
            
    def errorOut(self):
        self.errorvalue = True

    
#    def setInitialPosition(self, 0)

    # TODO Write method to home steppers for position "0"

    # TODO Write Method to move stepper to position (and include overload saftey)
    # TODO Determine if you should add a PositionChange Event handler
    #runs whenever there is a positional change

def StepperAttached():
    attached = self
    try:
        print("\nAttach Event Detected (Information Below)")
        print("===========================================")
        print("Library Version: %s" % attached.Stepper.getLibraryVersion())
        print("Serial Number: %d" % attached.Stepper.getDeviceSerialNumber())
        print("Channel: %d" % attached.Stepper.getChannel())
        print("Channel Class: %s" % attached.Stepper.getChannelClass())
        print("Channel Name: %s" % attached.Stepper.getChannelName())
        print("Device ID: %d" % attached.Stepper.getDeviceID())
        print("Device Version: %d" % attached.Stepper.getDeviceVersion())
        print("Device Name: %s" % attached.Stepper.getDeviceName())
        print("Device Class: %d" % attached.Stepper.getDeviceClass())
        print("\n")

    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Press Enter to Exit...\n")
        readin = sys.stdin.read(1)
        sys.exit(1)  

def StepperDetached():
    detached = self
    try:
        print("\nDetach event on Port %d Channel %d" % (detached.Stepper.getHubPort(), detached.Stepper.getChannel()))
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Press Enter to Exit...\n")
        readin = sys.stdin.read(1)
        sys.exit(1)   

def ErrorEvent(self, eCode, description):
    print("Error %i : %s" % (eCode, description))

def PositionChangeHandler(self, position):
    print("Position: %f" % position)


t = PhidgetStepper() #344986 -> (YSleds aka upper one) #343962->(XSleds aka lower one)
#b =  PhidgetStepper(344986)
#test.setCurrentLimit(.34)
#t.stepperSetup(15, 70, 4)
#b.stepperSetup(15, 70, 4)

#t.jog(20)
#b.jog(20)

#for i in range(1, 16*200):
#    test.jog(False, 1)
#    print i
#    sleep(.025)
#for i in range(100000):
#    test.jog(False)
#test.home()

