// перчатки
#define gloves_keys 8 //число кнорпок в каждой комнате
#define gloves_len 6 //число кнопок на экране. Обязетельно четное
byte gloves_map0[gloves_keys]; // кнопки в 1-й комнате. Нужно для перемешивания. Для кода берутся первые N
byte gloves_map1[gloves_keys]; // кнопки в 1-й комнате. Нужно для перемешивания. Для кода берутся первые N
byte gloves_map[gloves_len]; // Итоговый код
byte gloves_pos[gloves_len]; // Расположение символов на экране
String gloves_pr_code = "";//предыдущий символ
int gloves_active = -1;

void gloves_clear() {
  myNex_command("tm0.en=1");
  // myNex_writeNum("gloves.pic", 69 + lg);
  myNex_writeNum("p11.pic", 78 + lg);
  myNex_command("vis p11,1");
  myNex_writeNum("n0.val", -3);
  gloves_active = -1;
}

int gloves_img_by_code(int val) {
  val = ((val > 10) ? gloves_keys : 0) + (val % 10);
  return 84 + val * 2;
}

void gloves_show(byte n) {
  if (n == 0) {
    for (byte i = 3;i < 8;i++) {
      myNex_command("vis p" + String(i) + ",0");
    }
    myNex_writeNum("gloves.pic", 75 + lg);
  }

  myNex_writeNum("k" + String(gloves_pos[n - 1]) + ".pic", gloves_img_by_code(gloves_map[n - 1]) + 1);
  if (n < gloves_len) {
    myNex_writeNum("k" + String(gloves_pos[n]) + ".pic", gloves_img_by_code(gloves_map[n]));
    myNex_command("vis k" + String(gloves_pos[n]) + ",1");
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
    gloves_clear();
    return;
  }


  gloves_active++;
  gloves_show(gloves_active);
  if (gloves_active == gloves_len) { // завершение
    send("finish_3");
    gloves_active = -1;
    myNex_writeNum("p14.pic", 81 + lg);
    myNex_command("vis p14,1");
  }
}

void updateGlovesCode() {
  //Сгенерировать код
  gloves_active = 0;
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
  gloves_active = 0;
  myNex_command("tm0.en=0");
  gloves_show(0);

  send(out);
  // Serial.print("new code: ");
  // Serial.println(out);
  // Serial.print("\xFF\xFF\xFF");
}


void serialGloves(String inData) {
  if (gloves_active==-1){
    updateGlovesCode();
  }else{

  }
}

bool getGloves(String currentLine) {
  int j = currentLine.indexOf("GET /gloves");
  if (j >= 0) {
    updateGloves(currentLine.substring(j + 13, j + 15));
    return true;
  }
  return false;
}