#include <Arduino.h>

String readString;
char incomingByte;
int num;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
float incoming_value;
 unsigned char buffer[4];

 // If we read enough bytes, unpacked it
 if (Serial.readBytes(buffer, sizeof(float)) == sizeof(float)) {
     memcpy(&incoming_value, buffer, sizeof(float));
     Serial.print(incoming_value);
     }
}

  
