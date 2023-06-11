// ввод кода
#define MIN_GEN_PERIOD 4000 // время на отведенное на ввод кода
#define GAME_TIMER 9 // время на отведенное на ввод кода
byte keys_map[] = { 0,1,2,3,4,5,6,7,8,9 }; // клавиатура. каждый раз перемешивается
byte keys_code[] = { 0,0,0,0,0,0 }; // верная комбинация
byte keys_code_read[] = { 0,0,0,0,0,0 }; // полученная комбинация
int key_pos = 0; // текущий символ
byte pass_valid = 1;
long last_code_gen = 0;

byte code_game_state = 0; // этап игры. 0 - генерация пароля. 1 - ввод пароля. 2 - финал
byte code_game_timer = 0;
byte code_game_timer_div = 0;

void updateCode() {
  if (last_code_gen > millis()) return;
  int_write(0x5001, 0);
  go_to_page(17);
  code_game_timer = 10;
  code_game_state = 0;
  code_game_timer_div = 0;

  last_code_gen = millis() + MIN_GEN_PERIOD;
  key_pos = 0;
  pass_valid = 1;

  for (byte j = 0;j < 10;j++) {
    keys_map[j] = j;
  }

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
    int_write(0x6100+j*16,keys_code[j]);  //передаем код
    int_write(0x6203+j*16,0x0000);        //сброс цвета
  }
  delay(100);

  for (byte j = 0;j < 10;j++) {
    byte i = j + random(10 - j);
    byte c = keys_map[i];
    keys_map[i] = keys_map[j];
    keys_map[j] = c;
  }
  for (byte j = 0;j < 10;j++) {
    int_write(0x6000+j*16,keys_map[j]%10); //передаем клавиши
  }
  send(out);
}

void codesLoop(){
  code_game_timer_div++;
  // Serial.print(code_game_timer_div);
  // Serial.print(" ");
  // Serial.println(code_game_timer);

  if (code_game_state==0){
    if (code_game_timer_div>=2){
      code_game_timer_div=0;
      code_game_timer--;
      if (code_game_timer){
        int_write(0x5001,10-code_game_timer);
      }else{
        int_write(0x5001,GAME_TIMER);
        go_to_page(15);
        code_game_timer=GAME_TIMER;
        code_game_state=1;
      }
    }
    return;
  }
  if (code_game_state==1){
    if (code_game_timer_div>=10){
      code_game_timer_div=0;
      code_game_timer--;
      if (code_game_timer){
        int_write(0x5001,code_game_timer);
      }else{
        updateCode();
      }
    }
    return;
  }
}

void serialCodes() {
  if (code_game_state!=1) return;
  if (Buffer[4] == 0X63 && Buffer[5] == 0X00 && Buffer[6] == 0X01 && key_pos < 5) {
    keys_code_read[key_pos] = keys_map[Buffer[8]];
    int_write(0x6203+key_pos*16,(keys_code_read[key_pos] == keys_code[key_pos]) ? 0x07E0 : 0xF800);        //задаем цвет
    if (keys_code_read[key_pos] != keys_code[key_pos])pass_valid = 0;
    key_pos++;
    String out = "code_p:";
    for (byte j = 0;j < key_pos;j++) {
      out += String(keys_code_read[j]);
    }
    send(out);
    if (key_pos == 5 && pass_valid) {
      go_to_page(18);
      code_game_timer=0;
      code_game_state=2;
      send("finish_2");
    }
  }
}