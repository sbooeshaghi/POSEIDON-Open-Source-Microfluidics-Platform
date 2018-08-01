#!/usr/bin/env python
# -*- coding: utf-8 -*-

import serial
import time
import glob
import sys
from datetime import datetime
import time
# This gets the Qt stuff
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, QRunnable, pyqtSlot, QThreadPool, QObject, pyqtSignal
import cv2
import numpy as np

# This is our window from QtCreator
import poseidon_controller_gui

import traceback, sys

# ##############################
# MULTITHREADING : SIGNALS CLASS
# ##############################
class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)

# #############################
# MULTITHREADING : WORKER CLASS
# #############################
class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and 
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done

            print("Job completed")

# #####################################
# ERROR HANDLING : CANNOT CONNECT CLASS
# #####################################
class CannotConnectException(Exception):
	pass

# #######################
# GUI : MAIN WINDOW CLASS
# #######################
class MainWindow(QMainWindow, poseidon_controller_gui.Ui_MainWindow):

	# =======================================================
	# INITIALIZING : The UI and setting some needed variables
	# =======================================================
	def __init__(self):

		# Setting the UI to a class variable and connecting all GUI Components
		super(MainWindow, self).__init__()
		self.ui = poseidon_controller_gui.Ui_MainWindow()
		self.ui.setupUi(self)

		self.populate_syringe_sizes()
		self.populate_pump_jog_delta()
		self.populate_pump_units()
		self.setting_variables()
		self.populate_ports()
		

		
		self.connect_all_gui_components()
		self.grey_out_components()

		# Declaring start, mid, and end marker for sending code to Arduino
		self.startMarker = 60# <
		self.endMarker = 62  # ,F,0.0>
		self.midMarker = 124 # |

		# Initializing multithreading to allow parallel operations
		self.threadpool = QThreadPool()
		print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
		self.timer = QTimer()
		self.timer.setInterval(1000)
		self.timer.timeout.connect(self.recurring_timer)
		self.timer.start()
		self.counter = 0

		# Random other things I need
		self.image = None
		

	def recurring_timer(self):
		self.counter +=1

	# =============================
	# SETTING : important variables
	# =============================
	def setting_variables(self):

		self.set_p1_syringe()
		self.set_p2_syringe()
		self.set_p3_syringe()



		self.set_p1_units()
		self.set_p2_units()
		self.set_p3_units()

		self.is_p1_active = False
		self.is_p2_active = False
		self.is_p3_active = False

		
		#self.set_p2_speed()
		#self.set_p3_speed()

		#self.set_p1_accel()
		#self.set_p2_accel()
		#self.set_p3_accel()

		#self.set_p1_setup_jog_delta()
		#self.set_p2_setup_jog_delta()
		#self.set_p3_setup_jog_delta()


	# ===================================
	# CONNECTING : all the GUI Components
	# ===================================
	def connect_all_gui_components(self):

		# ~~~~~~~~~~~~~~~
		# MAIN : MENU BAR
		# ~~~~~~~~~~~~~~~
		self.ui.load_settings_BTN.triggered.connect(self.load_settings)
		self.ui.save_settings_BTN.triggered.connect(self.save_settings)

		# ~~~~~~~~~~~~~~~~
		# TAB : Controller
		# ~~~~~~~~~~~~~~~~

		# Px active checkboxes
		self.ui.p1_activate_CHECKBOX.stateChanged.connect(self.toggle_p1_activation)
		self.ui.p2_activate_CHECKBOX.stateChanged.connect(self.toggle_p2_activation)
		self.ui.p3_activate_CHECKBOX.stateChanged.connect(self.toggle_p3_activation)

		# Px display (TODO)

		# Px syringe display
		self.ui.p1_syringe_DROPDOWN.currentIndexChanged.connect(self.display_p1_syringe)
		self.ui.p2_syringe_DROPDOWN.currentIndexChanged.connect(self.display_p2_syringe)
		self.ui.p3_syringe_DROPDOWN.currentIndexChanged.connect(self.display_p3_syringe)

		# Px speed display
		self.ui.p1_units_DROPDOWN.currentIndexChanged.connect(self.display_p1_speed)
		self.ui.p2_units_DROPDOWN.currentIndexChanged.connect(self.display_p2_speed)
		self.ui.p3_units_DROPDOWN.currentIndexChanged.connect(self.display_p3_speed)
		#self.populate_pump_units()

		# Px amount
		self.ui.p1_amount_INPUT.valueChanged.connect(self.set_p1_amount)
		self.ui.p2_amount_INPUT.valueChanged.connect(self.set_p2_amount)
		self.ui.p3_amount_INPUT.valueChanged.connect(self.set_p3_amount)

		# Px jog delta
		#self.ui.p1_jog_delta_INPUT.valueChanged.connect(self.set_p1_jog_delta)
		#self.ui.p2_jog_delta_INPUT.valueChanged.connect(self.set_p2_jog_delta)
		#self.ui.p3_jog_delta_INPUT.valueChanged.connect(self.set_p3_jog_delta)

		# Action buttons
		self.ui.run_BTN.clicked.connect(self.run)
		self.ui.pause_BTN.clicked.connect(self.pause)
		self.ui.zero_BTN.clicked.connect(self.zero)
		self.ui.stop_BTN.clicked.connect(self.stop)
		self.ui.jog_plus_BTN.clicked.connect(lambda:self.jog(self.ui.jog_plus_BTN))
		self.ui.jog_minus_BTN.clicked.connect(lambda:self.jog(self.ui.jog_minus_BTN))

		# Set coordinate system
		self.ui.absolute_RADIO.toggled.connect(lambda:self.set_coordinate(self.ui.absolute_RADIO))
		self.ui.incremental_RADIO.toggled.connect(lambda:self.set_coordinate(self.ui.incremental_RADIO))

		# ~~~~~~~~~~~~
		# TAB : Camera
		# ~~~~~~~~~~~~

		# Setting camera action buttons
		self.ui.camera_connect_BTN.clicked.connect(self.start_camera)
		self.ui.camera_disconnect_BTN.clicked.connect(self.stop_camera)
		self.ui.camera_capture_image_BTN.clicked.connect(self.save_image)

		# ~~~~~~~~~~~
		# TAB : Setup
		# ~~~~~~~~~~~

		# Port, first populate it then connect it
		#self.populate_ports()
		self.ui.refresh_ports_BTN.clicked.connect(self.refresh_ports)
		self.ui.port_DROPDOWN.currentIndexChanged.connect(self.set_port)

		# Set the log file name
		self.date_string =  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		self.date_string = self.date_string.replace(":","_") # Replace semicolons with underscores
		#self.log_file_name = self.ui.log_file_name_INPUT.text() + "_" + self.date_string + ".txt"
		#self.ui.log_file_name_INPUT.textEdited.connect(self.set_log_file_name)

		# Px syringe size, populate then connect
		#self.populate_syringe_sizes()
		self.ui.p1_syringe_DROPDOWN.currentIndexChanged.connect(self.set_p1_syringe)
		self.ui.p2_syringe_DROPDOWN.currentIndexChanged.connect(self.set_p2_syringe)
		self.ui.p3_syringe_DROPDOWN.currentIndexChanged.connect(self.set_p3_syringe)

		# Px units
		self.ui.p1_units_DROPDOWN.currentIndexChanged.connect(self.set_p1_units)
		self.ui.p2_units_DROPDOWN.currentIndexChanged.connect(self.set_p2_units)
		self.ui.p3_units_DROPDOWN.currentIndexChanged.connect(self.set_p3_units)

		# Px speed
		self.ui.p1_speed_INPUT.valueChanged.connect(self.set_p1_speed)
		self.ui.p2_speed_INPUT.valueChanged.connect(self.set_p2_speed)
		self.ui.p3_speed_INPUT.valueChanged.connect(self.set_p3_speed)

		# Px accel
		self.ui.p1_accel_INPUT.valueChanged.connect(self.set_p1_accel)
		self.ui.p2_accel_INPUT.valueChanged.connect(self.set_p2_accel)
		self.ui.p3_accel_INPUT.valueChanged.connect(self.set_p3_accel)

		# Px jog delta (setup)
		self.ui.p1_setup_jog_delta_INPUT.currentIndexChanged.connect(self.set_p1_setup_jog_delta)
		self.ui.p2_setup_jog_delta_INPUT.currentIndexChanged.connect(self.set_p2_setup_jog_delta)
		self.ui.p3_setup_jog_delta_INPUT.currentIndexChanged.connect(self.set_p3_setup_jog_delta)

		# Px send settings
		self.ui.p1_setup_send_BTN.clicked.connect(self.send_p1_settings)
		self.ui.p2_setup_send_BTN.clicked.connect(self.send_p2_settings)
		self.ui.p3_setup_send_BTN.clicked.connect(self.send_p3_settings)

		# Connect to arduino
		self.ui.connect_BTN.clicked.connect(self.connect)
		self.ui.disconnect_BTN.clicked.connect(self.disconnect)

		# Send all the settings at once
		self.ui.send_all_BTN.clicked.connect(self.send_all)

	def grey_out_components(self):
		# ~~~~~~~~~~~~~~~~
		# TAB : Controller
		# ~~~~~~~~~~~~~~~~
		self.ui.run_BTN.setEnabled(False)
		self.ui.pause_BTN.setEnabled(False)
		self.ui.zero_BTN.setEnabled(False)
		self.ui.stop_BTN.setEnabled(False)
		self.ui.jog_plus_BTN.setEnabled(False)
		self.ui.jog_minus_BTN.setEnabled(False)

		# ~~~~~~~~~~~~~~~~
		# TAB : Setup
		# ~~~~~~~~~~~~~~~~
		self.ui.p1_setup_send_BTN.setEnabled(False)
		self.ui.p2_setup_send_BTN.setEnabled(False)
		self.ui.p3_setup_send_BTN.setEnabled(False)
		self.ui.send_all_BTN.setEnabled(False)

	def ungrey_out_components(self):
		# ~~~~~~~~~~~~~~~~
		# TAB : Controller
		# ~~~~~~~~~~~~~~~~
		self.ui.run_BTN.setEnabled(True)
		self.ui.pause_BTN.setEnabled(True)
		self.ui.zero_BTN.setEnabled(True)
		self.ui.stop_BTN.setEnabled(True)
		self.ui.jog_plus_BTN.setEnabled(True)
		self.ui.jog_minus_BTN.setEnabled(True)

		# ~~~~~~~~~~~~~~~~
		# TAB : Setup
		# ~~~~~~~~~~~~~~~~
		self.ui.p1_setup_send_BTN.setEnabled(True)
		self.ui.p2_setup_send_BTN.setEnabled(True)
		self.ui.p3_setup_send_BTN.setEnabled(True)
		self.ui.send_all_BTN.setEnabled(True)
	# ======================
	# FUNCTIONS : Controller
	# ======================

	def toggle_p1_activation(self):
		if self.ui.p1_activate_CHECKBOX.isChecked():
			self.is_p1_active = True
		else:
			self.is_p1_active = False

	def toggle_p2_activation(self):
		if self.ui.p2_activate_CHECKBOX.isChecked():
			self.is_p2_active = True
		else:
			self.is_p2_active = False

	def toggle_p3_activation(self):
		if self.ui.p3_activate_CHECKBOX.isChecked():
			self.is_p3_active = True
		else:
			self.is_p3_active = False

	# Get a list of active pumps (IDK if this is the best way to do this)
	def get_active_pumps(self):
		pumps_list = [self.is_p1_active, self.is_p2_active, self.is_p3_active]
		active_pumps = [i+1 for i in range(len(pumps_list)) if pumps_list[i]]
		return active_pumps

	def display_p1_syringe(self):
		self.ui.p1_syringe_LABEL.setText(self.ui.p1_syringe_DROPDOWN.currentText())
	def display_p2_syringe(self):
		self.ui.p2_syringe_LABEL.setText(self.ui.p2_syringe_DROPDOWN.currentText())
	def display_p3_syringe(self):
		self.ui.p3_syringe_LABEL.setText(self.ui.p3_syringe_DROPDOWN.currentText())

	def display_p1_speed(self):
		self.ui.p1_units_LABEL.setText(str(self.p1_speed) + " " + self.ui.p1_units_DROPDOWN.currentText())
	def display_p2_speed(self):
		self.ui.p2_units_LABEL.setText(str(self.p2_speed) + " " + self.ui.p2_units_DROPDOWN.currentText())
	def display_p3_speed(self):
		self.ui.p3_units_LABEL.setText(str(self.p3_speed) + " " + self.ui.p3_units_DROPDOWN.currentText())

	# Set Px distance to move
	def set_p1_amount(self):
		self.p1_amount = self.ui.p1_amount_INPUT.value()
	def set_p2_amount(self):
		self.p2_amount = self.ui.p2_amount_INPUT.value()
	def set_p3_amount(self):
		self.p3_amount = self.ui.p3_amount_INPUT.value()

	# Set Px jog delta
	#def set_p1_jog_delta(self):
	#	self.p1_jog_delta = self.ui.p1_jog_delta_INPUT.value()
	#def set_p2_jog_delta(self):
	#	self.p2_jog_delta = self.ui.p2_jog_delta_INPUT.value()
	#def set_p3_jog_delta(self):
	#	self.p3_jog_delta = self.ui.p3_jog_delta_INPUT.value()

	# Set the coordinate system for the pump
	def set_coordinate(self, radio):
		if radio.text() == "Abs.":
			if radio.isChecked():
				self.coordinate = "absolute"
		if radio.text() == "Incr.":
			if radio.isChecked():
				self.coordinate = "incremental"

	def run(self):
		self.statusBar().showMessage("You clicked Run")
		testData = []

		active_pumps = self.get_active_pumps()
		if len(active_pumps) > 0:

			p1_input_displacement = str(self.convert_displacement(self.p1_amount, self.p1_units, self.p1_syringe_area))
			p2_input_displacement = str(self.convert_displacement(self.p2_amount, self.p2_units, self.p2_syringe_area))
			p3_input_displacement = str(self.convert_displacement(self.p3_amount, self.p3_units, self.p3_syringe_area))

			pumps_2_run = ''.join(map(str,active_pumps))
			
			cmd = "<RUN,DIST,"+pumps_2_run+",0.0,F," + p1_input_displacement + "," + p2_input_displacement + "," + p3_input_displacement + ">"

			testData.append(cmd)

			worker = Worker(self.runTest, testData)

			print("Sending Jog Information")
			time.sleep(3)
			self.threadpool.start(worker)
			#self.runTest(testData)
				#send jog forward command
		else:
			self.statusBar().showMessage("No pumps enabled.")


	def pause(self):
		testData = []
		cmd = "<RESUME,BLAH,BLAH,BLAH,F,0.0,0.0,0.0>"
		testData.append(cmd)
		worker = Worker(self.runTest, testData)
		self.threadpool.start(worker)

	def resume(self):
		cmd = "<RESUME,BLAH,BLAH,BLAH,F,0.0,0.0,0.0>"
		testData.append(cmd)
		worker = Worker(self.runTest, testData)
		self.threadpool.start(worker)

	def zero(self):
		self.statusBar().showMessage("You clicked Zero")
		testData = []

		cmd = "<ZERO,BLAH,BLAH,BLAH,F,0.0,0.0,0.0>"
		
		worker = Worker(self.runTest, testData)
		print("Sending Setup Information")
		time.sleep(3)
		self.threadpool.start(worker)

	def stop(self):
		cmd = "<STOP,BLAH,BLAH,BLAH,F,0.0,0.0,0.0>"

		worker = Worker(self.send_single_command, cmd)
		print("Stopping")
		self.threadpool.start(worker)

	def jog(self, btn):
		#self.serial.flushInput()
		testData = []
		active_pumps = self.get_active_pumps()
		if len(active_pumps) > 0:
			pumps_2_run = ''.join(map(str,active_pumps))

			one_jog = str(self.p1_setup_jog_delta_to_send)
			two_jog = str(self.p2_setup_jog_delta_to_send)
			three_jog = str(self.p3_setup_jog_delta_to_send)
				 
			if btn.text() == "Jog +":
				f_cmd = "<RUN,DIST," + pumps_2_run +",0,F," + one_jog + "," + two_jog + "," + three_jog + ">"
				testData.append(f_cmd)

				worker = Worker(self.runTest, testData)

				print("Sending Jog Information")
				#time.sleep(3)
				self.threadpool.start(worker)
				#send jog forward command
			if btn.text() == "Jog -":
				#add optional argument for direction
				b_cmd = "<RUN,DIST," + pumps_2_run +",0,B," + one_jog + "," + two_jog + "," + three_jog + ">"
				testData.append(b_cmd)

				worker = Worker(self.runTest, testData)

				print("Sending Jog Information")
				#time.sleep(3)
				self.threadpool.start(worker)
				#send jog forward command
		else:
			self.statusBar().showMessage("No pumps enabled.")

	# ======================
	# FUNCTIONS : Camera
	# ======================

	# Initialize the camera
	def start_camera(self):
		camera_port = 0
		self.capture = cv2.VideoCapture(camera_port)
		#TODO check the native resolution of the camera and scale the size down here
		self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)
		self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 400)

		self.timer = QTimer(self)
		self.timer.timeout.connect(self.update_frame)
		self.timer.start(5)

	# Update frame function
	def update_frame(self):
		ret, self.image = self.capture.read()
		self.image = cv2.flip(self.image, 1)
		self.display_image(self.image, 1)

	# Display image in frame
	def display_image(self, image, window=1):
		qformat = QtGui.QImage.Format_Indexed8
		if len(image.shape) == 3: #
			if image.shape[2] == 4:
				qformat = QtGui.QImage.Format_RGBA8888
				
			else:
				qformat = QtGui.QImage.Format_RGB888
				print(image.shape[0], image.shape[1], image.shape[2])
		self.img_2_display = QtGui.QImage(image, image.shape[1], image.shape[0], image.strides[0], qformat)
		self.img_2_display = QtGui.QImage.rgbSwapped(self.img_2_display)

		if window == 1:
			self.ui.imgLabel.setPixmap(QtGui.QPixmap.fromImage(self.img_2_display))
			self.ui.imgLabel.setScaledContents(False)

	# Save image to set location
	def save_image(self):
		# Create a date string
		self.date_string =  datetime.now().strftime("%Y-%m-%d %H:%M:%S")

		# Replace semicolons with underscores
		self.date_string = self.date_string.replace(":","_")
		self.write_image_loc = './images/'+self.date_string + '.png'
		cv2.imwrite(self.write_image_loc, self.image)
		self.statusBar().showMessage("Captured Image, saved to: " + self.write_image_loc)


	# Stop camera
	def stop_camera(self):
		self.timer.stop()

	# ======================
	# FUNCTIONS : Setup
	# ======================

	# Populate the available ports
	def populate_ports(self):
	    """
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
	    self.ui.port_DROPDOWN.addItems(result)

	# Refresh the list of ports
	def refresh_ports(self):
		self.ui.port_DROPDOWN.clear()
		self.populate_ports()

	# Set the port that is selected from the dropdown menu
	def set_port(self):
		self.port = self.ui.port_DROPDOWN.currentText()

	# Set the name of the log file
	def set_log_file_name(self):
		r"""
		Sets the file name for the current test run, enables us to log data to the file.        

		Callback setter method from the 'self.ui.logFileNameInput' to set the 
		name of the log file. The log file name is of the form 
		label_Year-Month-Date hour_min_sec.txt
		"""
		# Create a date string
		self.date_string =  datetime.now().strftime("%Y-%m-%d %H:%M:%S")

		# Replace semicolons with underscores
		self.date_string = self.date_string.replace(":","_")

		self.log_file_name = self.ui.log_file_name_INPUT.text() + "_" + self.date_string + ".png"

	def save_settings(self):
		name, _ = QFileDialog.getSaveFileName(self,'Save File', options=QFileDialog.DontUseNativeDialog)

		# Create a date string
		self.date_string =  datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		# Replace semicolons with underscores
		self.date_string = self.date_string.replace(":","_")

		date_string = self.date_string

		# write all of the settings here
		## Settings for pump 1
		p1_syringe = str(self.p1_syringe)
		p1_units = str(self.p1_units)
		p1_speed = str(self.p1_speed)
		p1_accel = str(self.p1_accel)
		p1_setup_jog_delta = str(self.p1_setup_jog_delta)
		print(p1_setup_jog_delta)

		## Settings for pump 2
		p2_syringe = str(self.p2_syringe)
		p2_units = str(self.p2_units)
		p2_speed = str(self.p2_speed)
		p2_accel = str(self.p2_accel)
		p2_setup_jog_delta = str(self.p2_setup_jog_delta)

		## Settings for pump 3
		p3_syringe = str(self.p3_syringe)
		p3_units = str(self.p3_units)
		p3_speed = str(self.p3_speed)
		p3_accel = str(self.p3_accel)
		p3_setup_jog_delta = str(self.p3_setup_jog_delta)

		text = []
		text.append("File name: " + name + "\n") 				# line 0
		text.append("Date time: " + date_string + "\n") 		# line 1

		text.append(":================================ \n") 	# line 2
		text.append("P1 Syrin: " + p1_syringe + "\n") 			# line 3
		text.append("P1 Units: " + p1_units + "\n") 			# line 4
		text.append("P1 Speed: " + p1_speed + "\n") 			# line 5
		text.append("P1 Accel: " + p1_accel + "\n") 			# line 6
		text.append("P1 Jog D: " + p1_setup_jog_delta + "\n") 	# line 7
		text.append(":================================ \n")		# line 8
		text.append("P2 Syrin: " + p2_syringe + "\n") 			# line 9
		text.append("P2 Units: " + p2_units + "\n") 			# line 10
		text.append("P2 Speed: " + p2_speed + "\n") 			# line 11
		text.append("P2 Accel: " + p2_accel + "\n") 			# line 12
		text.append("P2 Jog D: " + p2_setup_jog_delta + "\n") 	# line 13
		text.append(":================================ \n") 	# line 14
		text.append("P3 Syrin: " + p3_syringe + "\n") 			# line 15
		text.append("P3 Units: " + p3_units + "\n") 			# line 16
		text.append("P3 Speed: " + p3_speed + "\n") 			# line 17
		text.append("P3 Accel: " + p3_accel + "\n") 			# line 18
		text.append("P3 Jog D: " + p3_setup_jog_delta + "\n") 	# line 19

		with open(name, 'w') as f:
			f.writelines(text)

	def load_settings(self):
		# need to make name an tupple otherwise i had an error and app crashed
		name, _ = QFileDialog.getOpenFileName(self, 'Open File', options=QFileDialog.DontUseNativeDialog)

		with open(name, 'r') as f:
			text = f.readlines()
			# here is where you load all of your variables
			# reformatting the text
			text = [line.split(':')[-1].strip('\n')[1:] for line in text]
			print(text)
			fname = text[0]
			date_string = text[1]

			p1_syringe = text[3]
			p1_units = text[4]
			p1_speed = text[5]
			p1_accel = text[6]
			p1_setup_jog_delta = text[7]

			p2_syringe = text[9]
			p2_units = text[10]
			p2_speed = text[11]
			p2_accel = text[12]
			p2_setup_jog_delta = text[13]

			p3_syringe = text[15]
			p3_units = text[16]
			p3_speed = text[17]
			p3_accel = text[18]
			p3_setup_jog_delta = text[19]

			#print(fname, date_string, p1_syringe, p1_units, p1_speed, p1_accel, p1_setup_jog_delta)

		p1_syringe_index = self.ui.p1_syringe_DROPDOWN.findText(p1_syringe, QtCore.Qt.MatchFixedString)
		self.ui.p1_syringe_DROPDOWN.setCurrentIndex(p1_syringe_index)
		p1_units_index = self.ui.p1_units_DROPDOWN.findText(p1_units, QtCore.Qt.MatchFixedString)
		self.ui.p1_units_DROPDOWN.setCurrentIndex(p1_units_index)
		self.ui.p1_speed_INPUT.setValue(float(p1_speed))
		self.ui.p1_accel_INPUT.setValue(float(p1_accel))
		print('==================')
		print("This is the jog: ", p1_setup_jog_delta)
		print('type: ', str(type(p1_setup_jog_delta)))
		print('==================')
		AllItems = [self.ui.p1_setup_jog_delta_INPUT.itemText(i) for i in range(self.ui.p1_setup_jog_delta_INPUT.count())]
		print("This is the list of jogs: ",AllItems)

		p1_setup_jog_delta_index = self.ui.p1_setup_jog_delta_INPUT.findText(p1_setup_jog_delta, QtCore.Qt.MatchFixedString)
		
		print("p1_setup_jog_delta_index is: ",p1_setup_jog_delta_index)
		self.ui.p1_setup_jog_delta_INPUT.setCurrentIndex(p1_setup_jog_delta_index)


		p2_syringe_index = self.ui.p2_syringe_DROPDOWN.findText(p2_syringe, QtCore.Qt.MatchFixedString)
		self.ui.p2_syringe_DROPDOWN.setCurrentIndex(p2_syringe_index)
		p2_units_index = self.ui.p2_units_DROPDOWN.findText(p2_units, QtCore.Qt.MatchFixedString)
		self.ui.p2_units_DROPDOWN.setCurrentIndex(p2_units_index)
		self.ui.p2_speed_INPUT.setValue(float(p2_speed))
		self.ui.p2_accel_INPUT.setValue(float(p2_accel))

		p2_setup_jog_delta_index = self.ui.p2_setup_jog_delta_INPUT.findText(p2_setup_jog_delta, QtCore.Qt.MatchFixedString)
		self.ui.p2_setup_jog_delta_INPUT.setCurrentIndex(p2_setup_jog_delta_index)


		p3_syringe_index = self.ui.p3_syringe_DROPDOWN.findText(p3_syringe, QtCore.Qt.MatchFixedString)
		self.ui.p3_syringe_DROPDOWN.setCurrentIndex(p3_syringe_index)
		p3_units_index = self.ui.p3_units_DROPDOWN.findText(p3_units, QtCore.Qt.MatchFixedString)
		self.ui.p3_units_DROPDOWN.setCurrentIndex(p3_units_index)
		self.ui.p3_speed_INPUT.setValue(float(p3_speed))
		self.ui.p3_accel_INPUT.setValue(float(p3_accel))

		p3_setup_jog_delta_index = self.ui.p3_setup_jog_delta_INPUT.findText(p3_setup_jog_delta, QtCore.Qt.MatchFixedString)
		self.ui.p3_setup_jog_delta_INPUT.setCurrentIndex(p3_setup_jog_delta_index)

		self.statusBar().showMessage("Settings loaded from: " + text[1])


	# Populate the list of possible syringes to the dropdown menus
	def populate_syringe_sizes(self):
		self.syringe_options = ["BD 1 mL", "BD 3 mL", "BD 5 mL", "BD 10 mL", "BD 20 mL", "BD 30 mL", "BD 60 mL"]
		self.syringe_volumes = [1, 3, 5, 10, 20, 30, 60]
		self.syringe_areas = [17.34206347, 57.88559215, 112.9089185, 163.539454, 285.022957, 366.0961536, 554.0462538]

		self.ui.p1_syringe_DROPDOWN.addItems(self.syringe_options)
		self.ui.p2_syringe_DROPDOWN.addItems(self.syringe_options)
		self.ui.p3_syringe_DROPDOWN.addItems(self.syringe_options)

	# Set Px syringe
	def set_p1_syringe(self):
		self.p1_syringe = self.ui.p1_syringe_DROPDOWN.currentText()
		self.p1_syringe_area = self.syringe_areas[self.syringe_options.index(self.p1_syringe)]
		self.display_p1_syringe()
	def set_p2_syringe(self):
		self.p2_syringe = self.ui.p2_syringe_DROPDOWN.currentText()
		self.p2_syringe_area = self.syringe_areas[self.syringe_options.index(self.p2_syringe)]
		self.display_p2_syringe()
	def set_p3_syringe(self):
		self.p3_syringe = self.ui.p3_syringe_DROPDOWN.currentText()
		self.p3_syringe_area = self.syringe_areas[self.syringe_options.index(self.p3_syringe)]
		self.display_p3_syringe()

	# Set Px units 
	def set_p1_units(self):
		self.p1_units = self.ui.p1_units_DROPDOWN.currentText()
		self.set_p1_speed()
		self.set_p1_accel()
		self.set_p1_setup_jog_delta()
		self.set_p1_amount()
	def set_p2_units(self):
		self.p2_units = self.ui.p2_units_DROPDOWN.currentText()
		self.set_p2_speed()
		self.set_p2_accel()
		self.set_p2_setup_jog_delta()
		self.set_p2_amount()
	def set_p3_units(self):
		self.p3_units = self.ui.p3_units_DROPDOWN.currentText()
		self.set_p3_speed()
		self.set_p3_accel()
		self.set_p3_setup_jog_delta()
		self.set_p3_amount()


	def populate_pump_units(self):
		print("I DID UNITS")
		self.units = ['mm/s', 'mL/s', 'mL/hr', 'µL/hr']
		self.ui.p1_units_DROPDOWN.addItems(self.units)
		self.ui.p2_units_DROPDOWN.addItems(self.units)
		self.ui.p3_units_DROPDOWN.addItems(self.units)

	def populate_pump_jog_delta(self):
		self.jog_delta = ['0.01', '0.1', '1.0', '10.0']
		print("I DID THIS")
		self.ui.p1_setup_jog_delta_INPUT.addItems(self.jog_delta)
		self.ui.p2_setup_jog_delta_INPUT.addItems(self.jog_delta)
		self.ui.p3_setup_jog_delta_INPUT.addItems(self.jog_delta)

	# Set Px speed TODO
	def set_p1_speed(self):
		self.p1_speed = self.ui.p1_speed_INPUT.value()
		self.ui.p1_units_LABEL.setText(str(self.p1_speed) + " " + self.ui.p1_units_DROPDOWN.currentText())
		self.p1_speed_to_send = self.convert_speed(self.p1_speed, self.p1_units, self.p1_syringe_area)

		#print(str(self.p1_speed) + " // " + str(self.p1_speed_to_send))
	def set_p2_speed(self):
		self.p2_speed = self.ui.p2_speed_INPUT.value()
		self.ui.p2_units_LABEL.setText(str(self.p2_speed) + " " + self.ui.p2_units_DROPDOWN.currentText())
		self.p2_speed_to_send = self.convert_speed(self.p2_speed, self.p2_units, self.p2_syringe_area)

		print(str(self.p2_speed) + " // " + str(self.p2_speed_to_send))
	def set_p3_speed(self):
		self.p3_speed = self.ui.p3_speed_INPUT.value()
		self.ui.p3_units_LABEL.setText(str(self.p3_speed) + " " + self.ui.p3_units_DROPDOWN.currentText())
		self.p3_speed_to_send = self.convert_speed(self.p3_speed, self.p3_units, self.p3_syringe_area)

		print(str(self.p3_speed) + " // " + str(self.p3_speed_to_send))

	# Set Px accel TODO
	def set_p1_accel(self):
		self.p1_accel = self.ui.p1_accel_INPUT.value()
		self.p1_accel_to_send = self.convert_accel(self.p1_accel, self.p1_units, self.p1_syringe_area)
		print(str(self.p1_accel) + " // " + str(self.p1_accel_to_send))
	def set_p2_accel(self):
		self.p2_accel = self.ui.p2_accel_INPUT.value()
		self.p2_accel_to_send = self.convert_accel(self.p2_accel, self.p2_units, self.p2_syringe_area)
	def set_p3_accel(self):
		self.p3_accel = self.ui.p3_accel_INPUT.value()
		self.p3_accel_to_send = self.convert_accel(self.p3_accel, self.p3_units, self.p3_syringe_area)

	# Set Px jog delta (setup) TODO
	def set_p1_setup_jog_delta(self):
		self.p1_setup_jog_delta = self.ui.p1_setup_jog_delta_INPUT.currentText()
		self.p1_setup_jog_delta = float(self.ui.p1_setup_jog_delta_INPUT.currentText())
		self.p1_setup_jog_delta_to_send = self.convert_displacement(self.p1_setup_jog_delta, self.p1_units, self.p1_syringe_area)
	def set_p2_setup_jog_delta(self):
		self.p2_setup_jog_delta = float(self.ui.p2_setup_jog_delta_INPUT.currentText())
		self.p2_setup_jog_delta_to_send = self.convert_displacement(self.p2_setup_jog_delta, self.p2_units, self.p2_syringe_area)
	def set_p3_setup_jog_delta(self):
		self.p3_setup_jog_delta = float(self.ui.p3_setup_jog_delta_INPUT.currentText())
		self.p3_setup_jog_delta_to_send = self.convert_displacement(self.p3_setup_jog_delta, self.p3_units, self.p3_syringe_area)

	# Send Px settings
	def send_p1_settings(self):
		self.p1_settings = []
		self.p1_settings.append("<SETTING,SPEED,1," + str(self.p1_speed_to_send) + ",F,0.0,0.0,0.0>")
		self.p1_settings.append("<SETTING,ACCEL,1," + str(self.p1_accel_to_send) + ",F,0.0,0.0,0.0>")
		self.p1_settings.append("<SETTING,DELTA,1," + str(self.p1_setup_jog_delta_to_send) + ",F,0.0,0.0,0.0>")

		worker = Worker(self.runTest, self.p1_settings)

		print("Sending P1 Setup Information")
		self.statusBar().showMessage("Sending P1 setup information.")
		self.threadpool.start(worker)
		
	def send_p2_settings(self):
		self.p2_settings = []
		self.p2_settings.append("<SETTING,SPEED,2," + str(self.p2_speed_to_send) + ",F,0.0,0.0,0.0>")
		self.p2_settings.append("<SETTING,ACCEL,2," + str(self.p2_accel_to_send) + ",F,0.0,0.0,0.0>")
		self.p2_settings.append("<SETTING,DELTA,2," + str(self.p2_setup_jog_delta_to_send) + ",F,0.0,0.0,0.0>")

		worker = Worker(self.runTest, self.p2_settings)

		print("Sending P2 Setup Information")
		self.statusBar().showMessage("Sending P2 setup information.")
		self.threadpool.start(worker)

	def send_p3_settings(self):
		self.p3_settings = []
		self.p3_settings.append("<SETTING,SPEED,3," + str(self.p3_speed_to_send) + ",F,0.0,0.0,0.0>")
		self.p3_settings.append("<SETTING,ACCEL,3," + str(self.p3_accel_to_send) + ",F,0.0,0.0,0.0>")
		self.p3_settings.append("<SETTING,DELTA,3," + str(self.p3_setup_jog_delta_to_send) + ",F,0.0,0.0,0.0>")

		worker = Worker(self.runTest, self.p3_settings)

		print("Sending P3 Setup Information")
		self.statusBar().showMessage("Sending P3 setup information.")
		self.threadpool.start(worker)

	# Connect to the Arduino board
	def connect(self):
		#self.port_nano = '/dev/cu.usbserial-A9M11B77'
		#self.port_uno = "/dev/cu.usbmodem1411"
		#self.baudrate = baudrate
		self.statusBar().showMessage("Attempting to connect to board..")
		try:
			port_declared = self.port in vars()
			try:
				
				self.serial = serial.Serial()
				self.serial.port = self.port
				self.serial.baudrate = 115200
				self.serial.parity = serial.PARITY_NONE
				self.serial.stopbits = serial.STOPBITS_ONE
				self.serial.bytesize = serial.EIGHTBITS
				self.serial.timeout = 1
				self.serial.open()
				self.wait_for_arduino()
				self.statusBar().showMessage("Successfully connected to board.")

				# ~~~~~~~~~~~~~~~~
				# TAB : Setup
				# ~~~~~~~~~~~~~~~~
				self.ui.disconnect_BTN.setEnabled(True)
				self.ui.p1_setup_send_BTN.setEnabled(True)
				self.ui.p2_setup_send_BTN.setEnabled(True)
				self.ui.p3_setup_send_BTN.setEnabled(True)
				self.ui.send_all_BTN.setEnabled(True)

				self.ui.connect_BTN.setEnabled(False)
			except:
				self.statusBar().showMessage("Cannot connect to board. Try again..")
				raise CannotConnectException
		except AttributeError:
			self.statusBar().showMessage("Please plug in the board and select a proper port, then press connect.")

	# Disconnect from the Arduino board
	def disconnect(self):
		self.serial.close()
		self.statusBar().showMessage("The board has been disconnected.")

		self.grey_out_components()
		self.ui.connect_BTN.setEnabled(True)
		self.ui.disconnect_BTN.setEnabled(False)

	# Send all settings
	def send_all(self):
		self.settings = []
		self.settings.append("<SETTING,SPEED,1,"+str(self.p1_speed_to_send)+",F,0.0,0.0,0.0>")
		self.settings.append("<SETTING,ACCEL,1,"+str(self.p1_accel_to_send)+",F,0.0,0.0,0.0>")
		self.settings.append("<SETTING,DELTA,1,"+str(self.p1_setup_jog_delta_to_send)+",F,0.0,0.0,0.0>")

		self.settings.append("<SETTING,SPEED,2,"+str(self.p2_speed_to_send)+",F,0.0,0.0,0.0>")
		self.settings.append("<SETTING,ACCEL,2,"+str(self.p2_accel_to_send)+",F,0.0,0.0,0.0>")
		self.settings.append("<SETTING,DELTA,2,"+str(self.p2_setup_jog_delta_to_send)+",F,0.0,0.0,0.0>")

		self.settings.append("<SETTING,SPEED,3,"+str(self.p3_speed_to_send)+",F,0.0,0.0,0.0>")
		self.settings.append("<SETTING,ACCEL,3,"+str(self.p3_accel_to_send)+",F,0.0,0.0,0.0>")
		self.settings.append("<SETTING,DELTA,3,"+str(self.p3_setup_jog_delta_to_send)+",F,0.0,0.0,0.0>")

		worker = Worker(self.runTest, self.settings)

		print("Sending all setup information")
		self.statusBar().showMessage("Sending all setup information.")
		self.threadpool.start(worker)
		self.ungrey_out_components()








	# =======================
	# MISC : Functions I need
	# =======================

	def steps2mm(self, steps):
	# 200 steps per rev
	# one rev is 0.8mm dist
		mm = steps/200/32*0.8
		return mm

	def steps2mL(self, steps, syringe_area):
		mL = self.mm32mL(self.steps2mm(steps)*syringe_area)
		return mL

	def steps2uL(self, steps, syringe_area):
		uL = self.mm32uL(self.steps2mm(steps)*syringe_area)
		return uL


	def mm2steps(self, mm):
		steps = mm/0.8*200*32
		return steps

	def mL2steps(self, mL, syringe_area):
		# note syringe_area is in mm^2
		steps = self.mm2steps(self.mL2mm3(mL)/syringe_area)
		return steps

	def uL2steps(self, uL, syringe_area):
		steps = self.mm2steps(self.uL2mm3(uL)/syringe_area)
		return steps


	def mL2uL(self, mL):
		return mL*1000.0

	def mL2mm3(self, mL):
		return mL*1000.0


	def uL2mL(self, uL):
		return uL/1000.0

	def uL2mm3(self, uL):
		return uL


	def mm32mL(self, mm3):
		return mm3/1000.0

	def mm32uL(self, mm3):
		return mm3

	def persec2permin(self, value_per_sec):
		value_per_min = value_per_sec*60.0
		return value_per_min

	def persec2perhour(self, value_per_sec):
		value_per_hour = value_per_sec*60.0*60.0
		return value_per_hour


	def permin2perhour(self, value_per_min):
		value_per_hour = value_per_min*60.0
		return value_per_hour

	def permin2persec(self, value_per_min):
		value_per_sec = value_per_min/60.0
		return value_per_sec


	def perhour2permin(self, value_per_hour):
		value_per_min = value_per_hour/60.0
		return value_per_min

	def perhour2persec(self, value_per_hour):
		value_per_sec = value_per_hour/60.0/60.0

	def convert_displacement(self, displacement, units, syringe_area):
		length = units.split("/")[0]
		time = units.split("/")[1]

		# convert length first
		if length == "mm":
			displacement = self.mm2steps(displacement)
		elif length == "mL":
			displacement = self.mL2steps(displacement, syringe_area)
		elif length == "µL":
			displacement = self.uL2steps(displacement, syringe_area)

		return displacement

	def convert_speed(self, speed, units, syringe_area):
		length = units.split("/")[0]
		time = units.split("/")[1]

		# convert length first
		if length == "mm":
			speed = self.mm2steps(speed)
		elif length == "mL":
			speed = self.mL2steps(speed, syringe_area)
		elif length == "µL":
			speed = self.uL2steps(speed, syringe_area)

		# convert time next
		if time == "s":
			pass
		elif time == "min":
			speed = self.permin2persec(speed)
		elif time == "hr":
			speed = self.perhour2persec(speed)

		return speed

	def convert_accel(self, accel, units, syringe_area):
		length = units.split("/")[0]
		time = units.split("/")[1]

		# convert length first
		if length == "mm":
			accel = self.mm2steps(accel)
		elif length == "mL":
			accel = self.mL2steps(accel, syringe_area)
		elif length == "µL":
			accel = self.uL2steps(accel, syringe_area)

		# convert time next
		if time == "s":
			pass
		elif time == "min":
			accel = self.permin2persec(self.permin2persec(accel))
		elif time == "hr":
			accel = self.perhour2persec(self.perhour2persec(accel))

		return accel


	'''
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
	'''










	#====================================== Reading and Writing to Arduino

	def sendToArduino(self, sendStr):
		self.serial.write(sendStr.encode())
		self.serial.flushInput()

	def recvFromArduino2(self):
		startMarker = self.startMarker
		midMarker = self.midMarker
		endMarker = self.endMarker
		i = 0
		ck = ""
		x = "z" # any value that is not an end- or startMarker
		byteCount = -1 # to allow for the fact that the last increment will be one too many
	  
		# wait for the start character
		while  ord(x) != startMarker: 
			x = self.serial.read()

		  
		# save data until the end marker is found
		while ord(x) != endMarker:
			if ord(x) == midMarker:
				i += 1
				print(ck)
				if i % 100 == 0:
					self.ui.p1_absolute_DISP.display(ck)
				ck = ""
				x = self.serial.read()

			if ord(x) != startMarker:
		    #print(x)
				ck = ck + x.decode()
				byteCount += 1

			x = self.serial.read()

		return(ck)

	def recvPositionArduino(self):
		startMarker = self.startMarker
		midMarker = self.midMarker
		endMarker = self.endMarker

		ck = ""
		x = "z" # any value that is not an end- or startMarker
		byteCount = -1 # to allow for the fact that the last increment will be one too many
	  
		# wait for the start character
		while  ord(x) != startMarker: 
			x = self.serial.read()
		  
		# save data until the end marker is found
		while ord(x) != endMarker:
			if ord(x) == midMarker:
				print(ck)
				self.ui.p1_absolute_DISP.display(ck)
				ck = ""
				x = self.serial.read()

			if ord(x) != startMarker:
		    #print(x)
				ck = ck + x.decode()
				byteCount += 1

			x = self.serial.read()

		return(ck)

	#============================

	def wait_for_arduino(self):
	   # wait until the Arduino sends 'Arduino Ready' - allows time for Arduino reset
	   # it also ensures that any bytes left over from a previous message are discarded
		startMarker = self.startMarker
		midMarker = self.midMarker
		endMarker = self.endMarker
		msg = ""
		while msg.find("Arduino is ready") == -1:
			while self.serial.inWaiting() == 0:
				pass
			msg = self.recvFromArduino2()
			print(msg + "\n")

	def runTest(self,td):
		numLoops = len(td)
		waitingForReply = False
		n = 0

		while n < numLoops:
			teststr = td[n]

			if waitingForReply == False:
				self.sendToArduino(teststr)
				print("Sent from PC -- LOOP NUM " + str(n) + " STR " + teststr)
				waitingForReply = True

			if waitingForReply == True:

				while self.serial.inWaiting() == 0:
					pass

				dataRecvd = self.recvFromArduino2()
				print("Reply Received -- " + dataRecvd)
				n += 1
				waitingForReply = False

				print("=============================\n\n")

			time.sleep(0.1)
		print("Send and receive complete\n\n")

	def send_single_command(self, command):
		waiting_for_reply = False
		if waiting_for_reply == False:
			self.sendToArduino(command)
			print("Sent from PC -- STR " + command)
			waiting_for_reply = True
		if waiting_for_reply == True:
			while self.serial.inWaiting() == 0:
				pass
			data_received = self.recvFromArduino2()
			print("Reply Received -- " + data_received)
			waiting_for_reply = False
			print("=============================\n\n")
			print("Sent a single command")



	def closeEvent(self, event):
		try:
			self.serial.close()
			self.threadpool.end()
		except AttributeError:
			pass
		sys.exit()

# I feel better having one of these
def main():
	# a new app instance
	app = QApplication(sys.argv)
	window = MainWindow()
	window.setWindowTitle("Poseidon Pumps Controller - Pachter Lab Caltech 2018")
	window.show()
	# without this, the script exits immediately.
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()


# "<SETTING,SPEED,1,80000,F,0.0,0.0,0.0>"
# "<SETTING,ACCEL,1,79999920,F,0.0,0.0,0.0>"
# "<SETTING,DELTA,1,80000.0,F,0.0,0.0,0.0>"

# "<SETTING,SPEED,2,80000.0,F,0.0,0.0,0.0>"
# "<SETTING,ACCEL,2,79999920.0,F,0.0,0.0,0.0>"
# "<SETTING,DELTA,2,80000.0,F,0.0,0.0,0.0>"

# "<SETTING,SPEED,3,80000.0,F,0.0,0.0,0.0>"
# "<SETTING,ACCEL,3,79999920.0,F,0.0,0.0,0.0>"
# "<SETTING,DELTA,3,80000.0,F,0.0,0.0,0.0>"

