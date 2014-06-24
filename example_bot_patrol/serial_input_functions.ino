/*
  getIntFromCommand
trim the command from the input string and convert what is left to an integer
------------------------------------------------------------------------------*/
unsigned int getIntFromCommand(String strInput, byte comlen){
  strInput = strInput.substring(comlen);
  char buf[16];
  strInput.toCharArray(buf, 16);
  return atoi(buf);
}


/*
  processSerialInput
process and serial input until a \n is recieved.  Then parse the input for a
valid command.  Then reset the input string
------------------------------------------------------------------------------*/
void processSerialInput(){
  while (Serial.available()) {  
    char inChar = (char)Serial.read(); 
    serialInputString += inChar;  // add it to the inputString
    if ((inChar=='\n' || inChar=='\r') && serialInputString.length() > 1) {
      Serial.print(">");
      Serial.println(serialInputString);
      
      if(serialInputString.startsWith("[")){ 
        outputStatus(); //"Robot Stuff"
        
      }
      
      serialInputString = "";  // clear the string
    }
  }
}
