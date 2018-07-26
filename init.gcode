; G-Code initialization file. This file contains settings that dictate the parameters you see below
; most of which are unimportant for this application. What is important are the steps/mm, max rates
; and acceleration. This are found in this way:
;
; 1) Determine the following parameters
;		a - numSteps = Number of steps per revolution of your motor (for my case using Nema 17) = 200
;		b - shaftPitch = pitch of the drive rod that the carriage is on (for my case M5x0.8mm pitch) = 0.8mm
;		c - microstepping = if you have a board that can do 1/32 (for example) microsteps, then this means
;			that the board can make the motor run at 200*32 steps per revolution. The parameter is that 
;			integer = 32
;
; 2) Perform the following multiplication
;		a - conversionFactor = numSteps*microstepping/shaftPitch (8000 for microstep, 250 for reg)
;		b - note that the units of conversion factor are [numSteps/mm] 
;
; 3) Note that $100, $101, $102 are the steps/mm for each axis (X, Y, Z). Set each of them equal to their
;	 respective conversionFactor that you calculated above. (if you are using the same motors are shaft 
;	 then each one is set to the same conversionFactor.)


G21;			metric
$0=10;			Step pulse, microseconds
$1=25;			Step idle delay, milliseconds
$2=0;			Step port invert, mask
$3=3;			Direction port invert, mask
$4=0;			Step enable invert, boolean
$5=0;			Limit pins invert, boolean
$6=0;			Probe pin invert, boolean
$10=3;			Status report, mask
$11=25.000;		Junction deviation, mm
$12=0.002;		Arc tolerance, mm
$13=0;			Report inches, boolean
$20=0;			Soft limits, boolean
$21=0;			Hard limits, boolean
$22=0;			Homing cycle, boolean
$23=0;			Homing dir invert, mask
$24=25.000;		Homing feed, mm/min
$25=500.000;	Homing seek, mm/min
$26=250;		Homing debounce, milliseconds
$27=1.000;		Homing pull-off, mm
$30=1000.;		Max spindle speed, RPM
$31=0;			Min spindle speed, RPM
$32=0;			Laser mode, boolean
$100=175;		X steps/mm
$101=250;		Y steps/mm
$102=500;		Z steps/mm
$110=10000.000;	X Max rate, mm/min
$111=10000.000;	Y Max rate, mm/min
$112=10000.000;	Z Max rate, mm/min
$120=75.000;	X Acceleration, mm/sec^2
$121=75.000;	Y Acceleration, mm/sec^2
$122=75.000;	Z Acceleration, mm/sec^2
$130=200.000;	X Max travel, mm
$131=200.000;	Y Max travel, mm
$132=200.000;	Z Max travel, mm
