#include <Arduino.h>
#include "MultiDriver.h"
#include "SyncDriver.h"

int setPoint = 55;
String str;

String readString;
char incomingByte;

// Motor steps per revolution. Most steppers are 200 steps or 1.8 degrees/step
#define MOTOR_STEPS 200
#define X_RPM 100
#define Y_RPM 100
#define Z_RPM 100

#define EN        8       // stepper motor enable, low level effective

#define X_DIR     5       //X axis, stepper motor direction control 
#define Y_DIR     6       //y axis, stepper motor direction control
#define Z_DIR     7       //zaxis, stepper motor direction control

#define X_STP     2       //x axis, stepper motor control
#define Y_STP     3       //y axis, stepper motor control
#define Z_STP     4       //z axis, stepper motor control

#define MICROSTEPS 32

/*
 * Choose one of the sections below that match your board
 */
#include "A4988.h"
#define MS1 10
#define MS2 11
#define MS3 12
//A4988 stepperX(MOTOR_STEPS, X_DIR, X_STP, EN, MS1, MS2, MS3);
//A4988 stepperY(MOTOR_STEPS, Y_DIR, Y_STP, EN, MS1, MS2, MS3);
//A4988 stepperZ(MOTOR_STEPS, Z_DIR, Z_STP, EN, MS1, MS2, MS3);

//BasicStepperDriver stepperX_tst(MOTOR_STEPS, X_DIR, X_STP);
//BasicStepperDriver stepperY_tst(MOTOR_STEPS, Y_DIR, Y_STP);
//BasicStepperDriver stepperZ_tst(MOTOR_STEPS, Z_DIR, Z_STP);

//MultiDriver controller(stepperX, stepperY, stepperZ);

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.write("Waiting for Raspberry Pi to send a signal...\n");
  pinMode(X_DIR, OUTPUT);
  pinMode(X_STP, OUTPUT);
  pinMode(Y_DIR, OUTPUT);
  pinMode(Y_STP, OUTPUT);
  pinMode(Z_DIR, OUTPUT); 
  pinMode(Z_STP, OUTPUT);
  
  pinMode(EN, OUTPUT);
  digitalWrite(EN, LOW);
  
//  stepperX.begin(X_RPM);
//  stepperY.begin(Y_RPM);
//  stepperZ.begin(Z_RPM);
//  
//  stepperX.setMicrostep(32);
//  stepperY.setMicrostep(32);
//  stepperZ.setMicrostep(32);
//  
//  stepperX.enable();
//  stepperY.enable();
//  stepperZ.enable();

//  stepperX_tst.begin(RPM, MICROSTEPS);
//  stepperY_tst.begin(RPM, MICROSTEPS);
//  stepperX_tst.enable();
//  stepperY_tst.enable();

}

void step(boolean dir, byte dirPin1, byte dirPin2, byte stepperPin1, byte stepperPin2, int steps)
{
  digitalWrite(dirPin1, dir);
  digitalWrite(dirPin2, dir);
  delay(50);
  Serial.print("Sending code to steppers right now \n");
  for (int i = 0; i < steps; i++) {
    digitalWrite(stepperPin1, HIGH);
    digitalWrite(stepperPin2, HIGH);
    delayMicroseconds(1000);  
    digitalWrite(stepperPin1, LOW);
    digitalWrite(stepperPin2, LOW);
    delayMicroseconds(250);  
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  char incomingByte;
  while (Serial.available()>0) {

   incomingByte = Serial.read(); // read byte

   readString += incomingByte;

   if(incomingByte == '\n'){
    step(false, X_DIR, Y_DIR, X_STP, Y_STP, 200*16*4); // x axis motor rotates CCW for 1 circle, as in 200 steps
  //step(false, Y_DIR, Y_STP, 3200); // y axis motor rotates CCW for 1 circle, as in 200 steps
  //step(false, Z_DIR, Z_STP, 3200); // z axis motor rotates CCW for 1 circle, as in 200 steps
    //stepperZ.rotate(360*4);
    //controller.rotate(360*4, 360*4, 360*1);
    Serial.print(readString);
    readString = "";
   }
  }
}

  
