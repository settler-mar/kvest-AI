#include "FastLED.h"
#include <IRremote.h>


/**
 * Команды управления
 * - reset - сброс в стартовое состояние
 * - name - вернет имя
 * - finish - перевести в коненое состояние 
 *
 * Сообщения состояния
 * - start - завпуск контроллера
 * - init - окончание инициализациии
 * - start - переведен в начальноес состояние
 * - error:N - состяние питния/флешки 
 * - progress:N - процесс наполнения шприца
 * - finish - задача окончена
 *
 * */

#define NAME "injectorBox"
String inData;

IRsend IrSender; //on 3 pin
#define UP_PIN 10 // реле для подъема шприца
#define DOWN_PIN 11 // реле для спуска шприца
#define CC_PIN 7 // Пин контроля тока
#define LED1_PIN 9 // Пин для индикатора "LOW POWER"
#define LED2_PIN 8 // Пин для индикатора "NO DATA"
#define WS_PIN  6 // Пин для светодиодов WS2812
#define PIN_KEY 2 // Ключ "Информация"
#define PIN_POWER_TEST A3 // Подача питания

#define STEP_DELAY 150 // Пауза между обработкой

#define WS_COUNT 30 // количество свотодиодов в линейке
#define WS_BLK_H_LEN 4 // Количество светодиодов в импульсе
#define WS_BLK_L_LEN 2 // Растояние между импульсами
#define WS_BLK_COLOR 200 // базовый цвет импульса
#define WS_BLK_COLOR_D 10 // разброс цвета
#define WS_BLK_COUNT 1 // Количество импульсоа для одной части шприца
#define INJECTOR_COUNT 10 // количество частей в шприце
#define ERR_SPEAD 2 // количество STEP_DELAY для мигания ошибкой
#define PAUSE_BEFORE_FINISH 1500

#define BRIGHTNESS 20 // яркость светодиодов
#define LED_TYPE    WS2812
#define COLOR_ORDER GRB
#define  WS_BLK_LEN (WS_BLK_H_LEN+WS_BLK_L_LEN) // общая длина импульса
struct CRGB leds[WS_COUNT];
byte ERR_st = 0;

byte ERR_last = 0;
/*
 * Алгоритм
 * 1) при старте запускается диагностика (шприц до упора вверх, потом вниз, контроль индикации)
 *
 */

byte mode = 1;
// 0 - ожидание
// 1 - demo/load up
// 2 - demo/load down
// 100 - finish

bool move_dir = false; // направление движения

int WS_step = 0; // смещение для ленты
int WS_step_tot = 0; //общее число прошедших шагов
int WS_step_max = WS_BLK_LEN * WS_BLK_COUNT * INJECTOR_COUNT - WS_BLK_L_LEN; //шагов для заполнения ленты

int blk_progress = 0; // прогрес для заливки 1го блока в шприц
byte inj_progress = 0; // блоков в шприце

void stop() {
  digitalWrite(UP_PIN, HIGH);
  digitalWrite(DOWN_PIN, HIGH);
}

void move(bool is_up) {
  digitalWrite(UP_PIN, !is_up);
  digitalWrite(DOWN_PIN, is_up);
  Serial.print("lift:");
  Serial.println(is_up ? 0 : 1);
  move_dir = is_up;
}


void test_cc() {
  byte CCState = digitalRead(CC_PIN);
  //Serial.println(CCState);
  if (CCState == HIGH) {
    //Serial.println("CC");
    Serial.print("lift:");
    Serial.println(move_dir ? 2 : 3);
    if (mode == 1) {
      move(false);
      mode = 2;
    }
    else {
      stop();
      if (mode == 2) {
        mode = 0;
      }
    }
  }
}

void send_ir() {
  unsigned long tData = 0xa90 + inj_progress;
  IrSender.sendSony(tData, 12);
}

//завершение алгоритма
void finish() {
  Serial.println("finish");
  inj_progress = INJECTOR_COUNT;
  send_ir();send_ir();send_ir();
  delay(PAUSE_BEFORE_FINISH);
  move(true);
  mode = 100;
}

//обработка лент
void WS_GO() {
  WS_step++;
  WS_step_tot++;
  int j = WS_step % WS_BLK_LEN;

  for (byte i = 0; i < WS_COUNT;i++) {
    if (
      j < WS_BLK_H_LEN and //Зажонный блок
      (WS_step_tot - i > 0) and //Начало потока
      (WS_step_tot - i < WS_step_max) //Конец потока*/
      ) {
      leds[i] = CHSV(WS_BLK_COLOR, 255, 255);
    }
    else {
      leds[i] = 0;
    }

    j--;
    if (j < 0) {
      j += WS_BLK_LEN;
    }
  }
  LEDS.show();

  if ((mode == 1) or (mode == 2)) {
    inj_progress++;
    Serial.print("progress:");
    Serial.println(inj_progress);
  }
  if (WS_step == WS_COUNT + WS_BLK_H_LEN) { //проверем что б окрашеная часть бока "залилась"
    blk_progress++;
    if (blk_progress >= WS_BLK_COUNT) { // проверем достаточно ли залили для 1-го блока шприца
      blk_progress -= WS_BLK_COUNT;
      inj_progress++;
      Serial.print("progress:");
      Serial.println(inj_progress);
      if (inj_progress >= INJECTOR_COUNT) { //Проверяем полный ли шприц
        if (mode == 0) {
          finish();
        }
        else {
          WS_step = 0;
          WS_step_tot = 0;
        }
      }
    }
  }
  if (WS_step >= WS_COUNT + WS_BLK_LEN) {
    WS_step -= WS_BLK_LEN;
  }

  if (inj_progress > INJECTOR_COUNT) {
    inj_progress = 0;
  }
}

void test_indictor(byte val, byte err_code) {
  if (ERR_last != err_code) {
    ERR_last = err_code;
    Serial.print("error:");
    Serial.println(err_code);
  }

  if (val == 0) {
    digitalWrite(LED1_PIN, LOW);
    digitalWrite(LED2_PIN, LOW);
    return;
  }

  ERR_st++;
  if (ERR_st > ERR_SPEAD * 2) {
    ERR_st = 0;
  }
  if (val == 2) {
    digitalWrite(LED1_PIN, HIGH);
    digitalWrite(LED2_PIN, LOW);
  }
  if (val == 1) {
    if (ERR_st > ERR_SPEAD) {
      digitalWrite(LED1_PIN, LOW);
      digitalWrite(LED2_PIN, HIGH);
    }
    else {
      digitalWrite(LED1_PIN, LOW);
      digitalWrite(LED2_PIN, LOW);
    }
  }
}

boolean test_control() { // Проверка условий работы; true если оба условаия выполнены.Если выполнены только одно то добавляем индикацию.
  int powerValue = analogRead(PIN_POWER_TEST);
  boolean Key_State = digitalRead(PIN_KEY);
  boolean power_state = (powerValue > 40);
  if (power_state) {
    delay(10);
    powerValue = analogRead(PIN_POWER_TEST);
    power_state = (powerValue > 45);
  }
  //Serial.println(powerValue);

  if (Key_State == power_state) { // Если статусы одинаковык то ввозвращаем их
    test_indictor(0, Key_State ? 0 : 3);
    return Key_State;
  }

  if (Key_State) {
    test_indictor(1, 1);
  }
  else {
    test_indictor(2, 2);
  }

  return false;// если статусы разные то возвращаем false
}

void demo() { // Режим диагностики
  test_cc();
  WS_GO();
  test_control();
  send_ir();
}

void start_state() { // Установить начатьное состояние
  digitalWrite(12, HIGH);
  digitalWrite(13, HIGH);
  stop();
  digitalWrite(LED1_PIN, LOW);
  digitalWrite(LED2_PIN, LOW);

  WS_step = 0;
  WS_step_tot = 0;
  blk_progress = 0;
  inj_progress = 0;
  mode = 0;
  Serial.print("progress:");
  Serial.println(inj_progress);

  for (int i = 0; i < WS_COUNT;i++) {
    leds[i] = 0;
  }
  LEDS.show();
  move(true);
}

void reset() {
  move(true);
  mode = 1;
  //Serial.println("Start DEMO");
  while (mode) {
    demo();
    delay(STEP_DELAY);
  }
  start_state();
  Serial.println("start");
}


void setup() {
  Serial.begin(9600);

  Serial.println("load");

  pinMode(UP_PIN, OUTPUT);
  pinMode(DOWN_PIN, OUTPUT);
  pinMode(LED1_PIN, OUTPUT);
  pinMode(LED2_PIN, OUTPUT);
  pinMode(PIN_KEY, OUTPUT);
  pinMode(CC_PIN, INPUT);
  digitalWrite(CC_PIN, LOW);

  pinMode(12, OUTPUT);
  pinMode(13, OUTPUT);

  LEDS.addLeds<LED_TYPE, WS_PIN, COLOR_ORDER>(leds, WS_COUNT);
  LEDS.setBrightness(BRIGHTNESS);
  start_state();

  while (!Serial)
    delay(500);

    //Serial.print(F("Ready to send IR signals at pin "));
    //Serial.println(IR_SEND_PIN);

  reset();

  Serial.println("init");
}

void readSerial() {
  if (Serial.available() > 0)
  {
    char recieved = Serial.read();
    if (recieved == '\n')
    {
      if (inData.startsWith("name")) {
        Serial.print("name:");
        Serial.println(NAME);
      }
      else if (inData.startsWith("reset")) {
        reset();
      }
      else if (inData.startsWith("start")) {
        move(false);
      }
      else if (inData.startsWith("finish")) {
        finish();
      }
      else if (inData.startsWith("up")) {
        mode = 0;
        move(true);
      }
      else if (inData.startsWith("down")) {
        mode = 0;
        move(false);
      }

      inData = ""; // Clear recieved buffer
    }
    else {
      inData += recieved;
    }
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  readSerial();
  test_cc();
  if (mode != 100) {
    if (test_control()) {
      WS_GO();
    }
    send_ir();
  }
  delay(STEP_DELAY);
}