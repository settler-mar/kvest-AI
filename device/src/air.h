byte air_pos[4];
String air_pos_st = "";
byte air_timer = 20;
unsigned long air_pr_time = 0;

void updateAir(String st) {
  air_pos_st = st.substring(0, 4);
  for (byte n = 0;n < 4;n++) {
    String s = st.substring(n, n + 1);
    air_pos[n] = s == "0" ? 0 : s == "2" ? 2 : 1;

    // Serial.print(n);
    // Serial.print(" ");
    // Serial.println(air_pos[n]); 
  }
}
void sendAir() {
  if (not start_game) return;
  byte airDors[] = { 0,1,2,3,2,3,0,1 };
  myNextion_cr();
  for (byte i = 2;i < 8;i++) {
    myNex_writeNum("p" + String(i) + ".pic", 3 + 3 * i + air_pos[airDors[i]]);
  }
}

void checkResultAir() {
  if (not start_game) return;
  if (air_timer >= 100) return;
  if (air_pos_st != "2020") {
    air_pr_time = 0;
    return;
  }
  if (air_pr_time == 0) {
    air_pr_time = millis() + 1000;
    return;
  }
  if (air_pr_time < millis()) {
    air_pr_time = 0;
    air_timer += 5;
    myNex_writeNum("n0.val", air_timer);
    if (air_timer == 90) {
      myNex_command("vis p0,1");
      myNex_writeNum("p0.pic", 3 + lg);
    }
    else   if (air_timer >= 90) {
      myNex_writeNum("p0.pic", 5 + lg);
      send("finish_1");
    }
  }
}

void serialAir(String inData) {
  if (inData.charAt(1) == 0x02 && inData.charAt(2) == 0x52) {
    start_game = true;
    sendAir();
  }
}

bool getAir(String currentLine) {
  int j = currentLine.indexOf("GET /air:");
  if (j >= 0) {
    updateAir(currentLine.substring(j + 9, j + 14));
    sendAir();
    updateLg();
    return true;
  }
  return false;
}