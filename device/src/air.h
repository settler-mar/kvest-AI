byte air_pos[4];
String air_pos_st = "";
byte air_timer = 20;
unsigned long air_pr_time = 0;

void updateAir(String st) {
  air_pos_st = st.substring(0, 4);
  for (byte n = 0;n < 4;n++) {
    String s = st.substring(n, n + 1);
    air_pos[n] = s == "0" ? 0 : s == "2" ? 2 : 1;
    Serial.print(n);
    Serial.print(" ");
    Serial.println(air_pos[n]); 
  }
}
void sendAir() {
  for (byte i = 0;i < 4;i++) {
    int_write(0x6310 + i, air_pos[i]);
  }
  int_write(0x6309, 1);
}
// 0x6310 - 0x6313 (VP) - заслонки
// 0x6314 - градусник (SP)
// 0x6330 - табличка (SP)

void checkResultAir() {
  if (not start_game) return;
  
  if (air_pr_time < millis()) {
    air_pr_time = millis() + 100;
    int_write(0x6314, air_timer + random(3));

    if (air_timer > 150) return;
    if (air_pos_st == "0220"){
      air_timer += 2;
    }else{
      return;
    }
    // myNex_writeNum("n0.val", air_timer);
    if (air_timer == 140) {
      // myNex_command("vis p0,1");
      // myNex_writeNum("p0.pic", 3 + lg);
      // int_write(0x6330+0x0A + i, air_pos[i]);
    }
    else   if (air_timer >= 150) {
      go_to_page(27);
      send("finish_1");
    }
  }
}

bool getAir(String currentLine) {
  int j = currentLine.indexOf("/air:");
  if (j >= 0) {
    updateAir(currentLine.substring(j + 5, j + 10));
    sendAir();
    return true;
  }
  return false;
}