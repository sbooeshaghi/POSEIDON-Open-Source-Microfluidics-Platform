String readString;
char incomingByte;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  char incomingByte;
  while (Serial.available()>0) {

   incomingByte = Serial.read(); // read byte

   readString += incomingByte;

   if(incomingByte == '\n'){
    Serial.print(readString);
    readString = "";
   }
  }
}

  
