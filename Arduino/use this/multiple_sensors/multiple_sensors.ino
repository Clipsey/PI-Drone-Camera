/*Ultra Sonic Sensor for multiple sensors and then transmit through USART

Circuit:
    +V at 5v
    GND at GND
    TRIG at PIN 7-
    ECHO at PIN 8+
    
    USART through PIN 0 and 1
*/

/*constant values for PINs for Ultra Sonic*/
/*Change constant for number of sensors*/
const unsigned int num_sensors = 4;

/*Redefine Ports here*/
const unsigned int TRIG_0 = 7;    //hard code first, then devise a loop
const unsigned int TRIG_1 = 6;
const unsigned int TRIG_2 = 5;
const unsigned int TRIG_3 = 4;
const unsigned int ECHO_0 = 8;
const unsigned int ECHO_1 = 9;
const unsigned int ECHO_2 = 10;
const unsigned int ECHO_3 = 11;
unsigned char trig_arr[] = {TRIG_0, TRIG_1, TRIG_2, TRIG_3};
unsigned char echo_arr[] = {ECHO_0, ECHO_1, ECHO_2, ECHO_3};

/*debug flag*/
bool debug = false;  //true for ascii, false for actual char in binary

/*Code*/
void setup(){
  //initialize serial communication: (USART)?
  Serial.begin(9600);
  //initialize ports to output/input
  pinMode(TRIG_0, OUTPUT);  //hard code first, then devise a loop
  pinMode(TRIG_1, OUTPUT);
  pinMode(TRIG_2, OUTPUT);
  pinMode(TRIG_3, OUTPUT);
  pinMode(ECHO_0, INPUT);
  pinMode(ECHO_1, INPUT);
  pinMode(ECHO_2, INPUT);
  pinMode(ECHO_3, INPUT);
}

 
//CM distance calculation. FINE TUNE THIS FOR BETTER ACCURACY
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

unsigned char loop_pulse(unsigned char i){  //i indicated which sensor
  long duration = 0;                //used to hold value of echo
  //Pulse
  digitalWrite(trig_arr[i], LOW);   //ensures off
  delayMicroseconds(2);             //moment of delay
  digitalWrite(trig_arr[i], HIGH);  //set high to pulse
  delayMicroseconds(10);            //needs to be on at least 10 uS for effective pulse
  digitalWrite(trig_arr[i], LOW);   //turn off
  
  //Echo
  duration = pulseIn(echo_arr[i], HIGH);  //calculates how long its receiving the pulse
  return uStoCM(duration);              //calculate result into cm
}
  
//unsigned char fix_percision(unsigned char cm){
//      static unsigned char prev;
//      static unsigned char second_prev;
//      unsigned char current;
//}

   
void loop(){   //main loop
  unsigned char cm;

  for (unsigned i=0; i<num_sensors; i++){
    cm = loop_pulse(i);
    
    if (!debug)
      Serial.write(cm);              //send binary to Raspberry Pi
    else{
      Serial.print("Sensor ");
      Serial.print(i+1);                //debug formatting, idc
      Serial.print(":[");
      Serial.print(cm);              //use for debugging, display char
      Serial.print("]\t");
    }
  }
    if (debug)
      Serial.println();              //used for debugging, display char newline
  delay(100);
}

  
  
  
  

