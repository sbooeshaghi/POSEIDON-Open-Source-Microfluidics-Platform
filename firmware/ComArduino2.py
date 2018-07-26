# 19 July 2014

# in case any of this upsets Python purists it has been converted from an equivalent JRuby program

# this is designed to work with ... ArduinoPC2.ino ...

# the purpose of this program and the associated Arduino program is to demonstrate a system for sending 
#   and receiving data between a PC and an Arduino.

# The key functions are:
#    sendToArduino(str) which sends the given string to the Arduino. The string may 
#                       contain characters with any of the values 0 to 255
#
#    recvFromArduino()  which returns an array. 
#                         The first element contains the number of bytes that the Arduino said it included in
#                             message. This can be used to check that the full message was received.
#                         The second element contains the message as a string


# the overall process followed by the demo program is as follows
#   open the serial connection to the Arduino - which causes the Arduino to reset
#   wait for a message from the Arduino to give it time to reset
#   loop through a series of test messages
#      send a message and display it on the PC screen
#      wait for a reply and display it on the PC

# to facilitate debugging the Arduino code this program interprets any message from the Arduino
#    with the message length set to 0 as a debug message which is displayed on the PC screen

# the message to be sent to the Arduino starts with < and ends with >
#    the message content comprises a string, an integer and a float
#    the numbers are sent as their ascii equivalents
#    for example <LED1,200,0.2>
#    this means set the flash interval for LED1 to 200 millisecs
#      and move the servo to 20% of its range

# receiving a message from the Arduino involves
#    waiting until the startMarker is detected
#    saving all subsequent bytes until the end marker is detected

# NOTES
#       this program does not include any timeouts to deal with delays in communication
#
#       for simplicity the program does NOT search for the comm port - the user must modify the
#         code to include the correct reference.
#         search for the lines 
#               serPort = "/dev/ttyS80"
#               baudRate = 9600
#               ser = serial.Serial(serPort, baudRate)
#


def steps2mm(steps):
  # 200 steps per rev
  # one rev is 0.8mm dist
  return steps/200*0.8

def mm2steps(mm):
  return mm/0.8*200


#=====================================

#  Function Definitions

#=====================================

def sendToArduino(sendStr):
  ser.write(sendStr.encode())


#======================================

def recvFromArduino():
  global startMarker, endMarker
  
  ck = ""
  x = "z" # any value that is not an end- or startMarker
  byteCount = -1 # to allow for the fact that the last increment will be one too many
  
  # wait for the start character
  while  ord(x) != startMarker: 
    x = ser.read()
  
  # save data until the end marker is found
  while ord(x) != endMarker:
    if ord(x) != startMarker:
      #print(x)
      ck = ck + x.decode()
      byteCount += 1
    x = ser.read()
  
  return(ck)

def recvFromArduino2():
  global startMarker, endMarker
  
  ck = ""
  x = "z" # any value that is not an end- or startMarker
  byteCount = -1 # to allow for the fact that the last increment will be one too many
  
  # wait for the start character
  while  ord(x) != startMarker: 
    x = ser.read()
  
  # save data until the end marker is found
  while ord(x) != endMarker:
    if ord(x) == midMarker:
      print(ck)
      ck = ""
      x = ser.read()

    if ord(x) != startMarker:
      #print(x)
      ck = ck + x.decode()
      byteCount += 1

    x = ser.read()

  return(ck)


#============================

def waitForArduino():

   # wait until the Arduino sends 'Arduino Ready' - allows time for Arduino reset
   # it also ensures that any bytes left over from a previous message are discarded
   
    global startMarker, endMarker
    
    msg = ""
    while msg.find("Arduino is ready") == -1:

      while ser.inWaiting() == 0:
        pass
        
      msg = recvFromArduino2()

      print(msg+'\n')
      
#======================================

def runTest(td):
  numLoops = len(td)
  waitingForReply = False

  n = 0
  while n < numLoops:

    teststr = td[n]

    if waitingForReply == False:
      sendToArduino(teststr)
      print("Sent from PC -- LOOP NUM " + str(n) + " TEST STR " + teststr)
      waitingForReply = True

    if waitingForReply == True:

      while ser.inWaiting() == 0:
        pass
        
      dataRecvd = recvFromArduino2()
      print("Reply Received -- " + dataRecvd)
      n += 1
      waitingForReply = False

      print("=============================\n\n")

    time.sleep(3)


def runTest2(td):
  numLoops = len(td)
  waitingForReply = False

  n = 0
  while n < numLoops:

    teststr = td[n]

    if waitingForReply == False:
      sendToArduino(teststr)
      print("Sent from PC -- LOOP NUM " + str(n) + " TEST STR " + teststr)
      waitingForReply = True

    if waitingForReply == True:
      while ser.inWaiting() == 0:
        pass
        
      dataRecvd = recContData()
      print("Reply Received -- " + dataRecvd)
      n += 1
      waitingForReply = False

      print("=============================\n\n")

    time.sleep(3)


#======================================

# THE DEMO PROGRAM STARTS HERE

#======================================

import serial
import time

print
print

# NOTE the user must ensure that the serial port and baudrate are correct
serPort = "/dev/cu.usbmodem1411"
baudRate = 115200
ser = serial.Serial(serPort, baudRate)
print("Serial port " + serPort + " opened  Baudrate " + str(baudRate))


startMarker = 60# <
endMarker = 62  # >
midMarker = 124 # |



waitForArduino()


testData = []
xSpeed = str(mm2steps(10)) # converts from mm/sec -> steps/sec
ySpeed = str(mm2steps(10))
zSpeed = str(mm2steps(10))

xAccel = str(mm2steps(10)) # converts from mm/sec^2 -> steps/sec^2
yAccel = str(mm2steps(10))
zAccel = str(mm2steps(10))

xDelta = str(mm2steps(10)) # converts from mm -> steps
yDelta = str(mm2steps(10))
zDelta = str(mm2steps(10))

xJog= str(mm2steps(10)) #converts from mm -> steps


print("Speed: ", xSpeed, "\n", "Accel: ", xAccel, "\n", "Delta: ", xDelta)




testData.append("<SETTING,SPEED,1," + xSpeed + ">") # Steps per second
#testData.append("<SETTING,SPEED,2,2000.0>") 
#testData.append("<SETTING,SPEED,3,2000.0>") 

testData.append("<SETTING,ACCEL,1," + xAccel + ">")
#testData.append("<SETTING,ACCEL,2,2000.0>")
#testData.append("<SETTING,ACCEL,3,2000.0>")

testData.append("<SETTING,DELTA,1," + xDelta + ">")
#testData.append("<SETTING,DELTA,2,6400.0>")
#testData.append("<SETTING,DELTA,3,1600.0>")

testData.append("<JOG,ONE,1," + xJog + ">")

# If you send jog one 0 then it will jog the delta that you set previously
#testData.append("<JOG,ALL,0,0>")
#testData.append("<RUN, 2, RUN, 0>")
#testData.append("<RUN, 3, RUN, 0>")


runTest(testData)


ser.close

# <Mode, Setting, Pump Num, Value>
# Mode can be Setup or Run
# Setting is max speed, accel, 

'''
<SETTING,SPEED,1,2000.0>
<SETTING,SPEED,2,2000.0>
<SETTING,SPEED,3,2000.0>

<SETTING,ACCEL,1,2000.0>
<SETTING,ACCEL,2,2000.0>
<SETTING,ACCEL,3,2000.0>

<RUN,RUN,1000000>
<RUN,RUN,1000000>
<RUN,RUN,1000000>

<SETTING,SPEED,1,2000.0>
<SETTING,ACCEL,1,2000.0>
<JOG,ONE,1,3200>

<RUN,RUN,1,10000>

<JOG,ONE,1,3200>

stepper1.distanceToGo() > 0


'''

