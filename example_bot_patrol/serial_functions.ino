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
      serialInputString.trim();
      Serial.print(">");
      Serial.println(serialInputString);
      
      if(serialInputString.startsWith("[") && serialInputString.endsWith("]")){ 
        serialInputString = serialInputString.substring(1,-1);
        
        byte botid = 0;
        int i = serialInputString.indexOf("],[");
        while(i > 0) {
          serialInputString = parsebotdata(serialInputString,i,botid);
          i = serialInputString.indexOf("],[");
          botid++;
        }
        i = serialInputString.indexOf("]");
        serialInputString = parsebotdata(serialInputString,i,botid);
        
        timeLastMessage = millis();
      }
      serialInputString = "";  // clear the string
    }
  }
}

String parsebotdata(String data, int i, byte botid) {
  String botdata = data.substring(1,i);
  char buf[6];
  String val;
  byte idx = 0;
  int j = botdata.indexOf(",");
  while(j > 0) {
    val = botdata.substring(0,j);
    val.toCharArray(buf, 6);
    Bot[botid][idx] = atoi(buf);
  
    botdata = botdata.substring(j+1);
    j = botdata.indexOf(",");
    idx++;
  }
  val = botdata.substring(0,j);
  val.toCharArray(buf, 6);
  Bot[botid][idx] = atoi(buf);
    
  if(data.length() > i+2) {
    data = data.substring(i+2);
  }
  
  return data;
}

void requestSerialData() {
  Serial.write("$W\n");
  return;
}
