// MultiStepper.pde
// -*- mode: C++ -*-
//
// Shows how to multiple simultaneous steppers
// Runs one stepper forwards and backwards, accelerating and decelerating
// at the limits. Runs other steppers at the same time
//
// Copyright (C) 2009 Mike McCauley
// $Id: MultiStepper.pde,v 1.1 2011/01/05 01:51:01 mikem Exp mikem $
#include <AccelStepper.h>
// Define some steppers and the pins the will use

// Motor steps per revolution. Most steppers are 200 steps or 1.8 degrees/step
#define MOTOR_STEPS 200
#define X_SPEED 200 // X steps per second
#define Y_SPEED 200 // Y
#define Z_SPEED 200 // Z

#define X_ACCEL 10000.0 // X steps per second per second
#define Y_ACCEL 10000.0 // Y
#define Z_ACCEL 10000.0 // Z

#define EN        8       // stepper motor enable, low level effective (note put jumper so automatic)

#define X_DIR     5       // X axis, direction pin 
#define Y_DIR     6       // Y 
#define Z_DIR     7       // Z

#define X_STP     2       // X axis, step pin
#define Y_STP     3       // Y
#define Z_STP     4       // Z

AccelStepper stepper1(AccelStepper::DRIVER, X_STP, X_DIR);
AccelStepper stepper2(AccelStepper::DRIVER, Y_STP, Y_DIR);
AccelStepper stepper3(AccelStepper::DRIVER, Z_STP, Z_DIR);


void setup()
{  
    stepper1.setMaxSpeed(X_SPEED);
    stepper2.setMaxSpeed(Y_SPEED);
    stepper3.setMaxSpeed(Z_SPEED);
    
    stepper1.setAcceleration(X_ACCEL);
    stepper2.setAcceleration(Y_ACCEL);
    stepper3.setAcceleration(Z_ACCEL);
    
    stepper1.move(1000);
    stepper2.move(1000);
    stepper3.move(1000); 
}
void loop()
{
    stepper1.runSpeed();
    stepper2.runSpeed();
    stepper3.runSpeed();
}
