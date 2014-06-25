#include "bot_id.h"
#include "pin_defs.h"
#include <Servo.h>

Servo LeftDrive, RightDrive;
#define LEFT_FWD 180
#define LEFT_STOP 90
#define LEFT_REV 0
#define RIGHT_FWD 0
#define RIGHT_STOP 90
#define RIGHT_REV 180
byte speed_L = LEFT_STOP;
byte speed_R = RIGHT_STOP;
unsigned long timeLastServoUpdate = 0;
unsigned long timeToStop = 0;
unsigned long timeToGo = 0;
unsigned long timeLastOutput = 0;

unsigned long timeLastMessage = 0;

String serialInputString = "";  // a string to hold incoming data

int Me[3] = {0,0,0};
int Target[3] = {0,0,0};

int headingTo = 0;
byte distanceTo = 0;
byte rotAmountTo = 0;
byte actionCount = 0;

boolean gameOn = false;

byte DestIndex = 255;
int Destinations[4][2] = {{8,8},{8,38},{62,38},{62,8}};

/*
  Setup
------------------------------------------------------------------------------*/
void setup(){
  LeftDrive.attach(LEFT_DRIVE_PIN);
  RightDrive.attach(RIGHT_DRIVE_PIN);
  pinMode(BUMP_SWITCH_RIGHT_PIN, INPUT);
  pinMode(BUMP_SWITCH_LEFT_PIN, INPUT);
  pinMode(STATUS_LED_PIN, OUTPUT);
  
  LeftDrive.write(LEFT_STOP);
  RightDrive.write(RIGHT_STOP);
  
  serialInputString.reserve(114); //28 per bot + 1 for the end char.
  Serial.begin(115200);
  Serial.println("example_bot: patrol");
  
  outputHelp();
  
}


/* 
  Main loop
------------------------------------------------------------------------------*/
void loop(){
  
  
  processSerialInput();
  
  //"Thought processes"
  //-------------------------------------------
  
  
  if(gameOn){
    
    if(Me[0]>0 || Me[1]>0){  //if my position is valid.
      if(DestIndex==255){
        DestIndex = whatPosClosest(Me);
      }
    
      //what is the distance to the Target point?
      distanceTo = distance(Me, Target);
      
      //what is the heading to the Target point?
      headingTo = 0; //int(16 + round( -Me.bearing(Target)/(PI/8) + (PI/16) ))%16; //convert the bearing to a heading of 0-15 increasing counter clockwise
      
      //if farther than 8 inches to Target
      if(distanceTo > 8 ){
        
        //what is the rotation direction and amount needed?
        int hdiff = (headingTo-Me[2]);
        if (hdiff==0){
          //I'm facing the right way to the Target point
          rotAmountTo = 0;
          if(timeToStop == 0 and timeToGo<millis()){
            //drive towards it.
            speed_L = throttle(LEFT_FWD, LEFT_STOP, 1.0);
            speed_R = throttle(RIGHT_FWD, RIGHT_STOP, 1.0);
            timeToStop = millis() + (1000*distanceTo/8);
            timeToGo = timeToStop + 900;
            actionCount++;
          }
        }else if (hdiff < -8 || (0 < hdiff && hdiff < 8)){
          //Turn left
          rotAmountTo = (16+abs(hdiff))%16;
          if (rotAmountTo > 0){
            //turn left then wait a little bit
            if(timeToStop == 0 and timeToGo<millis()){
              speed_L = throttle(LEFT_REV, LEFT_STOP, 0.1);
              speed_R = throttle(RIGHT_FWD, RIGHT_STOP, 0.1);
              timeToStop = millis() + (50*rotAmountTo);
              timeToGo = timeToStop + 900;
              actionCount++;
            }
          }
          
        }else{
          //Turn right
          rotAmountTo = (16-abs(hdiff))%16;
          if (rotAmountTo > 0){
            //turn right then wait a little bit
            if(timeToStop == 0 and timeToGo<millis()){
              speed_L = throttle(LEFT_FWD, LEFT_STOP, 0.1);
              speed_R = throttle(RIGHT_REV, RIGHT_STOP, 0.1);
              timeToStop = millis() + (50*rotAmountTo);
              timeToGo = timeToStop + 900;
              actionCount++;
            }
          }
        }
      }else{
        //withinrange of the current destination, set the nest one.
        DestIndex = (DestIndex+1)%4;
        Target[0] = Destinations[DestIndex][0];
        Target[1] = Destinations[DestIndex][1];
      }
      
    } //end valid Me position
    
    
    
  } //end game on
  
  
  //-------------------------------------------
  
  
  //Is it time to stop?  I consider this more of a reflex than thought.
  if(timeToStop > 0 && millis() >= timeToStop){
    Stop();
  }
  
  //if a bump switch is triggered backup
  if(!digitalRead(BUMP_SWITCH_RIGHT_PIN) || !digitalRead(BUMP_SWITCH_LEFT_PIN)){
    speed_L = LEFT_REV;
    speed_R = RIGHT_REV;
    timeToStop = millis() + 500;
    timeToGo = timeToStop + 1000;
  }
    
  //Update Servo positions  
  if(millis() - timeLastServoUpdate > 15){  //limit servo updating to every 15ms at most
    LeftDrive.write(speed_L);
    RightDrive.write(speed_R);
    timeLastServoUpdate = millis();
  }
  
  //Output various statuses and values once in a while.
  if(millis()-timeLastOutput > 1000){
    outputStatus();
    timeLastOutput = millis();
  }
  
  delay(1);
}
/*----------------------------------------------------------------------------*/


void Stop(){
  speed_L = LEFT_STOP;
  speed_R = RIGHT_STOP;
  timeToStop = 0;
  
  if(timeToGo <= millis()){
    actionCount = 0;
  }
}

int throttle(int Direction, int Stop, float Throttle){
  return int((Direction-Stop)*Throttle + Stop);
}

int distance(int pt0[], int pt1[]) {
  return sqrt(pow(pt1[0]-pt0[0],2)+pow(pt1[1]-pt0[1],2));
}

byte whatPosClosest(int p0[]){
  int p1[2] = {0,0};
  byte index = 0;
  byte closest = 255;
  for(byte i=0; i<4; i++){
    p1[0] = Destinations[i][0];
    p1[1] = Destinations[i][1];
    byte d = distance(p0, p1);
    if(d < closest){
      closest = d;
      index = i;
    }
  }
  return index;
}

