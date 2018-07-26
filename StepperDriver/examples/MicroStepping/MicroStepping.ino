/*
 * Microstepping demo
 *
 * This requires that microstep control pins be connected in addition to STEP,DIR
 *
 * Copyright (C)2015 Laurentiu Badea
 *
 * This file may be redistributed under the terms of the MIT license.
 * A copy of this license has been included with this distribution in the file LICENSE.
 */
#include <Arduino.h>
int setPoint = 55;
String readString;
String str;

// Motor steps per revolution. Most steppers are 200 steps or 1.8 degrees/step
#define MOTOR_STEPS 200
#define RPM 300

#define EN        8       // stepper motor enable, low level effective

#define X_DIR     5       //X axis, stepper motor direction control 
#define Y_DIR     6       //y axis, stepper motor direction control
#define Z_DIR     7       //zaxis, stepper motor direction control

#define X_STP     2       //x axis, stepper motor control
#define Y_STP     3       //y axis, stepper motor control
#define Z_STP     4       //z axis, stepper motor control

/*
 * Choose one of the sections below that match your board
 */
#include "A4988.h"
#define MS1 10
#define MS2 11
#define MS3 12
A4988 stepper(MOTOR_STEPS, Y_DIR, Y_STP, EN, MS1, MS2, MS3);

//#include "DRV8825.h"
//#define MODE0 10
//#define MODE1 11
//#define MODE2 12
//DRV8825 stepper(MOTOR_STEPS, Y_DIR, Y_STP, EN, MODE0, MODE1, MODE2);

void setup() {
    /*
     * Set target motor RPM.
     */
     Serial.begin(9600);
     Serial.write("Waiting for Raspberry Pi to send a signal...\n");
    stepper.begin(RPM);
    stepper.enable();
    
    // set current level (for DRV8880 only). 
    // Valid percent values are 25, 50, 75 or 100.
    // stepper.setCurrent(100);
}

void loop() {

    /*
     * Moving motor in full step mode is simple:
     */
    //stepper.setMicrostep(1);  // Set microstep mode to 1:1

    // One complete revolution is 360°
    //stepper.rotate(360);     // forward revolution
    //stepper.rotate(-360);    // reverse revolution

    // One complete revolution is also MOTOR_STEPS steps in full step mode
    //stepper.move(MOTOR_STEPS);    // forward revolution
    //stepper.move(-MOTOR_STEPS);   // reverse revolution

    //delay(1000);
    /*
     * Microstepping mode: 1, 2, 4, 8, 16 or 32 (where supported by driver)
     * Mode 1 is full speed.
     * Mode 32 is 32 microsteps per step.
     * The motor should rotate just as fast (at the set RPM),
     * but movement precision is increased, which may become visually apparent at lower RPMs.
     */
     
    //stepper.setMicrostep(16);   // Set microstep mode to 1:8

    // In 1:8 microstepping mode, one revolution takes 8 times as many microsteps
    //stepper.move(32 * MOTOR_STEPS);    // forward revolution
    // stepper.move(-8 * MOTOR_STEPS);   // reverse revolution
    
    // One complete revolution is still 360° regardless of microstepping mode
    // rotate() is easier to use than move() when no need to land on precise microstep position
    //stepper.rotate(-3600);
    //stepper.rotate(-360);
    if(Serial.available() > 1) {
      str = Serial.readStringUntil('\n');
    }
    Serial.write(str);

}
