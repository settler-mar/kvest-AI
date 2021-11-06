#ifndef debug_game
void myNex_writeNum(String compName, uint32_t val) {
  Serial.print(compName);
  Serial.print("=");
  Serial.println(val);
}

void myNex_writeStr(String command, String txt) {
  command = command;
  txt = txt;

  if (txt == "cmd") {
    Serial.println(command);
  }
  else if (txt != "cmd") {
    Serial.print(command);
    Serial.print("=\"");
    Serial.print(txt);
    Serial.println("\"");
  }
}

void myNex_command(String command) {
  Serial.println(command);
}

void myNextion_cr() {
}
#else
void myNex_writeNum(String compName, uint32_t val) {
  Serial.print(compName);
  Serial.print("=");
  Serial.print(val);
  Serial.print("\xFF\xFF\xFF");
}

void myNex_writeStr(String command, String txt) {
  command = command;
  txt = txt;

  if (txt == "cmd") {
    Serial.print(command);
    Serial.print("\xFF\xFF\xFF");

  }
  else if (txt != "cmd") {
    Serial.print(command);
    Serial.print("=\"");
    Serial.print(txt);
    Serial.print("\"");
    Serial.print("\xFF\xFF\xFF");
  }
}

void myNex_command(String command) {
  Serial.print(command);
  Serial.print("\xFF\xFF\xFF");
}

void myNextion_cr() {
  Serial.print("\xFF\xFF\xFF");
}
#endif