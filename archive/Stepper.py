import sys
import time 
from Phidget22.Devices.Stepper import *
from Phidget22.PhidgetException import *
from Phidget22.Phidget import *
from Phidget22.Net import *
class Stepper(object):
    def __jnit__(self:)
        try:
            self.ch = Stepper()
        except RuntimeError as e:
            print("Runtime Exception %s" % e.details)
            print("Press Enter to Exit...\n")
            readin = sys.stdin.read(1)
            sys.exit(1)
        

def StepperAttached(self):
    try:
        attached = self
        print("\nAttach Event Detected (Information Below)")
        print("===========================================")
        print("Library Version: %s" % attached.getLibraryVersion())
        print("Serial Number: %d" % attached.getDeviceSerialNumber())
        print("Channel: %d" % attached.getChannel())
        print("Channel Class: %s" % attached.getChannelClass())
        print("Channel Name: %s" % attached.getChannelName())
        print("Device ID: %d" % attached.getDeviceID())
        print("Device Version: %d" % attached.getDeviceVersion())
        print("Device Name: %s" % attached.getDeviceName())
        print("Device Class: %d" % attached.getDeviceClass())
        print("\n")

    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Press Enter to Exit...\n")
        readin = sys.stdin.read(1)
        sys.exit(1)   
    
def StepperDetached(self):
    detached = self
    try:
        print("\nDetach event on Port %d Channel %d" % (detached.getHubPort(), detached.getChannel()))
    except PhidgetException as e:
        print("Phidget Exception %i: %s" % (e.code, e.details))
        print("Press Enter to Exit...\n")
        readin = sys.stdin.read(1)
        sys.exit(1)   

def ErrorEvent(self, eCode, description):
    print("Error %i : %s" % (eCode, description))

def PositionChangeHandler(self, position):
    print("Position: %f" % position)

try:
    ch.setOnAttachHandler(StepperAttached)
    ch.setOnDetachHandler(StepperDetached)
    ch.setOnErrorHandler(ErrorEvent)

    ch.setOnPositionChangeHandler(PositionChangeHandler)

    print("Waiting for the Phidget Stepper Object to be attached...")
    ch.openWaitForAttachment(5000)
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Press Enter to Exit...\n")
    readin = sys.stdin.read(1)
    sys.exit(1)

print("Engaging the motor\n")
ch.setEngaged(1)

print("Setting Position to 15000 for 5 seconds...\n")
ch.setTargetPosition(15000)
time.sleep(5)

print("Setting Position to -15000 for 5 seconds...\n")
ch.setTargetPosition(-15000)
time.sleep(5)

print("Setting Position to 0 for 5 seconds...\n")
ch.setTargetPosition(0)
time.sleep(5)

try:
    ch.close()
except PhidgetException as e:
    print("Phidget Exception %i: %s" % (e.code, e.details))
    print("Press Enter to Exit...\n")
    readin = sys.stdin.read(1)
    sys.exit(1) 
print("Closed Stepper device")
sys.exit(0)
                     
