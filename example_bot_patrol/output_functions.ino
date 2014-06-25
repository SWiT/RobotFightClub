/*
  outputStatus
output important variables to the Serial port
------------------------------------------------------------------------------*/
void outputStatus(){
  Serial.println();
  unsigned long now = millis();
  Serial.print("now:");
  Serial.print(now);
  Serial.print("\ttimeToStop:");
  if (timeToStop > now)
  {
    Serial.print(timeToStop-now);
  }else{
    Serial.print(0);
  }
  
  Serial.print("\ttimeLastMessage:");
  Serial.print(now-timeLastMessage);
  Serial.println();
  
  Serial.print("Me: ");
  Serial.print(MY_BOT_ID);
  Serial.print(" (");
  Serial.print(Me[0]);
  Serial.print(", ");
  Serial.print(Me[1]);
  Serial.print(") H");
  Serial.print(Me[2]);
  Serial.print("\tL:");
  Serial.print(speed_L);
  Serial.print("\tR:");
  Serial.print(speed_R);
  Serial.println();
  
  Serial.print("Target: (");
  Serial.print(Target[0]);
  Serial.print(", ");
  Serial.print(Target[1]);
  Serial.print(") H");
  Serial.print(Target[2]);
  Serial.println();
  
  Serial.print("\tdistanceTo:");
  Serial.print(distanceTo);
  Serial.print("\theadingTo:");
  Serial.print(headingTo);
  Serial.print("\trotAmountTo:");
  Serial.print(rotAmountTo);
  Serial.print("\tactionCount:");
  Serial.print(actionCount);
  Serial.println();
  
  for (byte i=0; i<4; i++){
    outputBotStatus(i);
    Serial.println();
  } 
  Serial.println();
        
}


/*
  outputHelp
output the help menu to the Serial port
------------------------------------------------------------------------------*/
void outputHelp(){
  Serial.println("Help Menu:");
  Serial.println("--------------------------");
  Serial.println("'H'\tDisplay this Help Menu");
  Serial.println("'?'\tDisplay important status variables");
  Serial.println();
}


/*
  outputBotStatus
*/
void outputBotStatus(byte i){
  Serial.print(i);
  Serial.print(":()");
}
