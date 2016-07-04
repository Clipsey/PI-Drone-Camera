/*Ultra Sonic Sensor for multiple sensors and then transmit through USART

Circuit:
    +V at 5v
    GND at GND
    TRIG at PIN 7
    ECHO at PIN 8
    
    USART through PIN 0 and 1
*/

/*constant values for PINs for Ultra Sonic*/

const unsigned int TRIG_0 = 7;
const unsigned int TRIG_1 = 6;
const unsigned int ECHO_0 = 8;
const unsigned int ECHO_1 = 9;

void setup(){
  //initialize serial communication: (USART)?
  Serial.begin(9600);
}

void loop(){
  /*set TRIG_0 to OUTPUT PIN and ECHO_0 to INPUT PIN*/
  pinMode(TRIG_0, OUTPUT);  
  pinMode(ECHO_0, INPUT);
  pinMode(TRIG_1, OUTPUT);  
  pinMode(ECHO_1, INPUT);
  /*variables used to calculate distance with ultrasonic*/
  long duration; 
  unsigned char cm_0;
  unsigned char cm_1;
  
  /*set initially low and then pulse for 10 microseconds*/
  //write 0
  digitalWrite(TRIG_0, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_0, HIGH);
  delayMicroseconds(10);

  duration = pulseIn(ECHO_0, HIGH);
  cm_0 = uStoCM(duration);
  
  //write 1  
  digitalWrite(TRIG_1, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_1, HIGH);
  delayMicroseconds(10);
  

  duration = pulseIn(ECHO_1, HIGH);
  cm_1 = uStoCM(duration);
  
  Serial.write(cm_0);
  Serial.write(cm_1);
  //Serial.print("cm");
  //Serial.println();
  
  delay(100);
}
 
unsigned char uStoCM(long uS){
  /*29us per cm*/
  unsigned long temp;
  unsigned char result;
  
  temp = uS / 29 / 2;
  if (temp >= 255){
    result = 255;
  }
  else{
    result = temp;
  }
  return result;
}
  
  
  
  

