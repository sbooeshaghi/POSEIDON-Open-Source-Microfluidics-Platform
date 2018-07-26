#!/usr/bin/python
import serial
import signal
import syslog
import time


com_port = '/dev/cu.usbmodem1411'

X_STEP = 2
Y_STEP = 3
Z_STEP = 4

X_DIR = 5
Y_DIR = 6
Z_DIR = 7


from Arduino import Arduino

board = Arduino('9600') #plugged in via USB, serial com at rate 9600
board.pinMode(13, "OUTPUT")

while True:
    board.digitalWrite(13, "LOW")
    time.sleep(1)
    board.digitalWrite(13, "HIGH")
    time.sleep(1)

# stepper_pins = [X_STEP, Y_STEP, Z_STEP]
# steps_per_revolution = 200

# board = PyMata3(com_port=com_port, log_output=True, arduino_wait=5)
# time.sleep(3)
# board.send_reset()
# time.sleep(3)

# # label, type of connection, microstepping, enable pin present

# board.accelstepper_config(0, 1, 1, 0, [X_STEP, X_DIR])
# board.accelstepper_config(1, 1, 1, 0, [Y_STEP, Y_DIR])
# board.accelstepper_config(2, 1, 1, 0, [Z_STEP, Z_DIR])

# time.sleep(3)

# board.accelstepper_set_speed(0, 2000)
# board.accelstepper_set_speed(1, 2000)
# board.accelstepper_set_speed(2, 2000)
# time.sleep(3)
# board.accelstepper_step(0, 16*200, "forward")
# board.accelstepper_step(1, 16*200, "forward")
# board.accelstepper_step(2, 16*200, "forward")
# board.shutdown()

# def signal_handler(sig, frm):
#     print('You pressed Ctrl+C!!!!')
#     if firmata is not None:
#         firmata.send_reset()
#     sys.exit(0)


# if __name__=='__main__':
# board = PyMata3(com_port=com_port, log_output=True, arduino_wait=5)
# board.send_reset()

# signal.signal(signal.SIGINT, signal_handler)

# board.send_reset()
# board.accelstepper_config(0, 4, 16, 1, [X_STEP, DIR])
# board.accelstepper_config(1, 4, 16, 1, [Y_STEP, Y_DIR])
# board.accelstepper_config(2, 4, 16, 1, [Z_STEP, Z_DIR])

# time.sleep(1)

# board.accelstepper_set_speed(0, 200)
# board.accelstepper_set_speed(1, 200)
# board.accelstepper_set_speed(2, 200)

# board.accelstepper_step(0, 200)
# board.accelstepper_step(1, 200)
# board.accelstepper_step(2, 200)

#     # close firmata
# board.shutdown()
