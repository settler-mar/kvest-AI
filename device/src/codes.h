// ввод кода
byte keys_map[] = { 0,1,2,3,4,5,6,7,8,9 }; // клавиатура. каждый раз перемешивается
byte keys_code[] = { 0,0,0,0 }; // верная комбинация
byte keys_code_read[] = { 0,0,0,0 }; // полученная комбинация
int key_pos = 0; // текущий символ
byte pass_valid = 1;

void updateCode() {
  key_pos = 0;
  pass_valid = 1;
  myNex_writeNum("n5.val", 9);//запуск таймера
  for (byte j = 0;j < 5;j++) {
    byte i = j + random(10 - j);
    byte c = keys_map[i];
    keys_map[i] = keys_map[j];
    keys_map[j] = c;
  }
  String out = "code_r:";
  for (byte j = 0;j < 5;j++) {
    keys_code[j] = keys_map[j];
    out += String(keys_map[j]);
    myNex_writeStr("t" + String(j) + ".txt", String(keys_map[j]));//передаем код
    myNex_writeNum("t" + String(j) + ".pco", 0);                  //сброс цвета
  }
  for (byte j = 0;j < 10;j++) {
    byte i = j + random(10 - j);
    byte c = keys_map[i];
    keys_map[i] = keys_map[j];
    keys_map[j] = c;
  }

  for (byte j = 0;j < 10;j++) {
    myNex_writeStr("b" + String(j) + ".txt", String(keys_map[j]));//передаем клавиши
  }
  send(out);
  
}

void serialCodes(String inData) {
  if (inData.charAt(1) == 0x01 && inData.charAt(2) == 0x00) {
    updateCode();
  }
  if (inData.charAt(1) == 0x00 && key_pos < 5) {
    keys_code_read[key_pos] = keys_map[inData.charAt(2)];
    // myNex_command("vis b"+String(int(inData.charAt(2)))+",0");
    myNex_writeNum("t" + String(key_pos) + ".pco", (keys_code_read[key_pos] == keys_code[key_pos]) ? 2016 : 63488);
    if (keys_code_read[key_pos] != keys_code[key_pos])pass_valid = 0;
    key_pos++;
    String out = "code_p:";
    for (byte j = 0;j < key_pos;j++) {
      out += String(keys_code_read[j]);
    }
    send(out);
    if (key_pos == 5 && pass_valid) {
      Serial.print("\xFF\xFF\xFF");
      myNex_command("tm0.en=0");
      myNex_command("vis p0,1");
      send("finish_2");
    }
  }
}