// перчатки
#define gloves_keys 8 //число кнорпок в каждой комнате
#define gloves_len 6 //число кнопок на экране. Обязетельно четное
byte gloves_map0[gloves_keys]; // кнопки в 1-й комнате. Нужно для перемешивания. Для кода берутся первые N
byte gloves_map1[gloves_keys]; // кнопки в 1-й комнате. Нужно для перемешивания. Для кода берутся первые N
byte gloves_map[gloves_len]; // Итоговый код
byte gloves_pos[gloves_len]; // Расположение символов на экране
String gloves_pr_code = "";//предыдущий символ
int gloves_active = -1;
int gloves_timer = 0;
int gloves_time = 0;

void updateGlovesCode() {
  //Сгенерировать код
  // gloves_active = 0;
  gloves_pr_code = "";
  for (byte i = 0;i < gloves_keys;i++) {
    gloves_map0[i] = i;
    gloves_map1[i] = 10 + i;
  }

  for (byte j = 0;j < gloves_keys;j++) {
    byte i = j + random(gloves_keys - j);
    byte c = gloves_map0[i];
    gloves_map0[i] = gloves_map0[j];
    gloves_map0[j] = c;

    i = j + random(gloves_keys - j);
    c = gloves_map1[i];
    gloves_map1[i] = gloves_map1[j];
    gloves_map1[j] = c;
  }

  for (byte j = 0;j < gloves_len / 2;j++) {
    gloves_map[j * 2] = gloves_map0[j];
    gloves_map[j * 2 + 1] = gloves_map1[j];
    gloves_pos[j * 2] = j * 2;
    gloves_pos[j * 2 + 1] = j * 2 + 1;
  }

  String out = "code_s:";
  for (byte j = 0;j < gloves_len;j++) {
    byte i = j + random(gloves_len - j);
    byte c = gloves_map[i];
    gloves_map[i] = gloves_map[j];
    gloves_map[j] = c;

    out += String(c) + "_";

    i = j + random(gloves_len - j);
    c = gloves_pos[i];
    gloves_pos[i] = gloves_pos[j];
    gloves_pos[j] = c;
  }
  // gloves_active = 0;
  // myNex_command("tm0.en=0");
  //gloves_show(0);

  send(out);
  Serial.print("new code: ");
  Serial.println(out);
  // Serial.print("\xFF\xFF\xFF");
}

void gloves_clear() {
  go_to_page(28);
  int_write(0x5010+5, 6);
  int_write(0x5010+6, 8);

  for (byte i = 0; i < gloves_len; i++){
      int_write(0x5001 + i, 0);
  }

  gloves_active = -1;
  gloves_time = 0;
  gloves_timer = 0;

  updateGlovesCode();
}

void gloves_stop(){
  int_write(0x5010+5, 9);
  int_write(0x5010+6, 11);  
  gloves_active = gloves_len;
  gloves_time = 2;
  gloves_timer = 0;
}

void gloves_show(byte n, bool active) {
  if (n < gloves_len) {
    // byte code = gloves_map[n] + 1;
    byte code = ((gloves_map[n] > 10) ? gloves_keys : 0) + (gloves_map[n] % 10) + 1;
    Serial.print(n);
    Serial.print("_");
    Serial.print(active);
    Serial.print("_");
    if (active)code += 16;
    int_write(0x5001 + n, code);
    Serial.println(code);
  }
}

void updateGloves(String code) {//Входящий символ
  if (gloves_pr_code == code or gloves_active < 0) return;
  gloves_pr_code = code;
  String out = "code_g:";
  for (byte j = 0;j < gloves_active;j++) {
    out += String(gloves_map[j]) + "_";
  }
  out += code;
  send(out);

  if (gloves_map[gloves_active] != code.toInt()) {
    gloves_stop();
    return;
  }

  gloves_show(gloves_active, true);
  gloves_active++;
  gloves_show(gloves_active, false);
  if (gloves_active == gloves_len) { // завершение
    int_write(0x5010+5, 3);
    int_write(0x5010+6, 5);

    send("finish_3");
    gloves_active = gloves_len+1;
    // myNex_writeNum("p14.pic", 81 + lg);
    // myNex_command("vis p14,1");
  }
}


void serialGloves(String inData) {
}

bool getGloves(String currentLine) {
  int j = currentLine.indexOf("/gloves");
  if (j >= 0) {
    updateGloves(currentLine.substring(j + 9, j + 11));
    return true;
  }
  return false;
}

void glovesLoop(){
  if (gloves_active==-1){
    gloves_timer+=1;
    if (gloves_timer>=8){
      gloves_time+=1;
      gloves_timer=0;
      if (gloves_time<6) int_write(0x5000, gloves_time);
      if (gloves_time>=7){
        gloves_active = 0;
        gloves_show(0,false);
        go_to_page(29);
      }
    }
    return;
  }

  if (gloves_active==gloves_len){
    gloves_timer+=1;
    if (gloves_timer>=8){
      gloves_time+=1;
      gloves_timer=0;
      if (gloves_time>=3){
        gloves_clear();
      }
    }
    return;
  }
}