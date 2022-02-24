#include <Arduino.h>
#include <FastLED.h>
#include <ServoSmooth.h>
#include <IRremote.h>

ServoSmooth servo;

IRsend IrSender; //on 3 pin
// -------------------        Servo        -------------------------
#define servoPin 4   // пин к которому подключен серва
#define servoMin 40  // угол голова прямо
#define servoMax 150 // угол голова вбок
#define servoSpeed 200 // скорость сервы
#define servoAccel 0.2 // ускороение для сервы
// -------------------        IO setup     -------------------------
#define Undr_time 500
uint8_t btnPin[] = { 2 };
#define btn_cnt 1
unsigned long btnUndr[] = { 0 }; // андребизг для отправки сообщений

uint8_t relay[] = { 6,7 };
byte relayON[] = { 0,0 };
#define relay_cnt 2
#define relay_delay 500

uint8_t outPin[] = { 8, 9 };
bool pin_state[] = { false, false };
#define out_cnt 2
// -------------------     LEDS    -------------------------
#define START_INFO_CNT 40  // количество светодилдов с до головы
#define EXIT_INFO_CNT 40   // количество светодилдов с после головы
#define  INJECTION_CNT 20 // светодиодов в иньекции
#define LED_SPEED 120      // скорость с которой бегут светодиоды
#define LED_DATA 40       // соотношение заженных и нет светодиодов 0..100. Если 100 то будут все гореть
byte colors[] = { 0, // 0 - глаза "старт"
                  60, //1 - глаза "после"
                  70, //2 - до головы
                  10, //3 - после головы "старт"
                  120, // 4 - после головы "финиш"
                  220, // 5 - иньекция
                  180 // 6 - до головы "финиш"
};
#define COLOR_RANDOM 20    // разброс цветов относительно основоного (от база; до база + rand(COLOR_RANDOM))


#define LED_PIN     5
#define COLOR_ORDER GRB
#define CHIPSET     WS2811
#define NUM_LEDS    START_INFO_CNT + EXIT_INFO_CNT + 2
#define BRIGHTNESS  200
unsigned long ws_timer = 0;

// -------------------     C O N S T A N T S    -------------------------
// Central Plate serial
#define NAME "head"
String inData;

#define elif else if

// -------------------     V A R I A B L E S    -------------------------

byte btnState[] = { 255,255,255,255 };
CRGBArray<NUM_LEDS> leds;
CRGB color_start;
CRGB color_exit;
byte is_run = 0; // 0 - игра не запущенна; 1 - запущенна "голова вбок"; 2 - запущенна "голова прямо"; 3 - сделали иньекцию; 4 - иньекция дошла до головы; 5-Финиш
byte injection_counter = INJECTION_CNT;
byte inject_cnt = 0;
CRGB inject_color;

// -------------------     S E T U P    -------------------------

byte convertA2Pos(uint8_t pin) {
  int val = analogRead(pin);
  if (val <= 400) {
    return 0;
  }
  elif(val <= 800) {
    return 2;
  }
  else {
    return 1;
  }
}

void IR_send() {
  unsigned long tData = 0xa90;
  IrSender.sendSony(tData, 12);
}

void setPins(byte pin, boolean stat) {
  pin_state[pin] = stat;
  digitalWrite(outPin[pin], stat ? LOW : HIGH);
  Serial.print("digital");
  Serial.print(pin);
  Serial.print(":");
  Serial.println(stat ? 1 : 0);
}

void update_btn() {
  for (byte i = 0;i < btn_cnt;i++) {
    byte st = digitalRead(btnPin[i]);
    if (btnState[i] != st and btnUndr[i] < millis()) {
      btnUndr[i] = millis() + Undr_time;
      if (st) {
        if (i == 0) {
          // Вставили шприц
          if (is_run < 3) {
            is_run = 3;
            Serial.println("inject start");
            IR_send();
          }
        }
      }
      btnState[i] = st;
    }
  }
}


void reset() {
  is_run = 0;
  FastLED.clear();
  FastLED.show();
  for (byte i = 0;i < out_cnt;i++) {
    setPins(i, false);
  }
  servo.setTargetDeg(servoMin);
  injection_counter = INJECTION_CNT;
  inject_cnt = 0;
}

//обработка лент
void WS_GO() {
  if (ws_timer > millis()) return;
  ws_timer = millis() + LED_SPEED;

  // обновляем глаза
  if (is_run == 4) {
    leds[0] = 0;
  }
  else {
    CHSV hsv(colors[is_run < 4 ? 0 : 1] + random(COLOR_RANDOM), 100 + random(150), 255);
    hsv2rgb_rainbow(hsv, leds[0]);
  }
  leds[1] = leds[0];

  // двигаем все вперед на 1
  for (byte i = NUM_LEDS - 1; i > 2; i--) {
    leds[i] = leds[i - 1];
  }
  // обработка новых данных
  if (is_run == 3) {
    if (injection_counter > 0) {
    // Serial.print("make inject: ");
    // Serial.println(injection_counter);
      injection_counter--;
      leds[2] = inject_color;
      IR_send();
    }
    else {
      leds[2] = 0;
    }
  }
  else if (is_run != 4) {
    if (random(100) <= LED_DATA) {
      leds[2] = color_start;
    }
    else {
      CHSV hsv(colors[is_run == 5 ? 6 : 2] + random(COLOR_RANDOM), 255, 255);
      hsv2rgb_rainbow(hsv, color_start);
      leds[2] = 0;
    }
  }
  else {
    leds[2] = 0;
  }

  // обработка данных после голвы
  if (leds[2 + START_INFO_CNT]) {
    if (is_run != 4) {
      if (is_run == 3 and leds[2 + START_INFO_CNT] == inject_color) {
        inject_cnt++;
        // Serial.print("get inject: ");
        // Serial.println(inject_cnt);
        if (inject_cnt == INJECTION_CNT) {
          Serial.println("inject done");
          is_run = 4;
        }
        leds[2 + START_INFO_CNT] = 0;
      }
      else {
        leds[2 + START_INFO_CNT] = color_exit;
      }
    }
    else {
      leds[2 + START_INFO_CNT] = 0;
    }
  }
  else {
    if (is_run != 4) {
      CHSV hsv(colors[is_run == 5 ? 4 : 3] + random(COLOR_RANDOM), 255, 255);
      hsv2rgb_rainbow(hsv, color_exit);
    }
    else {
      leds[2 + START_INFO_CNT] = 0;
    }
  }

  FastLED.show();
}

void setup() {
  Serial.begin(9600);
  delay(500);
  FastLED.addLeds<CHIPSET, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(255);
  for (byte i = 0;i < NUM_LEDS;i++) {
    leds[i] = 0xFFFF00;
  }
  FastLED.show();
  delay(1000);
  FastLED.clear();
  FastLED.show();
  CHSV hsv(colors[5], 255, 255);
  hsv2rgb_rainbow(hsv, inject_color);

  for (byte i = 0;i < relay_cnt;i++) {
    pinMode(relay[i], OUTPUT);
    digitalWrite(relay[i], not relayON[i]);
  }

  for (byte i = 0;i < out_cnt;i++) {
    pinMode(outPin[i], OUTPUT);
    setPins(i, false);
  }

  for (byte i = 0; i < 3; i++)
  {
    pinMode(btnPin[i], INPUT);
  }

  servo.attach(servoPin);        // подключить
  servo.setSpeed(servoSpeed);    // ограничить скорость
  servo.setAccel(servoAccel);   	  // установить ускорение (разгон и торможение)

  reset();
  Serial.println("load");
  Serial.println("init");
}

void pulse(byte i) {
  if (i >= relay_cnt) return;
  digitalWrite(relay[i], relayON[i]);
  delay(relay_delay);
  digitalWrite(relay[i], not relayON[i]);
  Serial.print("pulse");
  Serial.println(i);
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
      }elif(inData.startsWith("reset")) {
        Serial.println("reset");
        reset();
      }elif(inData.startsWith("start")) {
        Serial.println("start");
        is_run = 1;
        servo.setTargetDeg(servoMax);
      }elif(inData.startsWith("wait")) {
        Serial.println("wait");
        is_run = 2;
        servo.setTargetDeg(servoMin);
      }elif(inData.startsWith("live")) {
        Serial.println("live");
        is_run = 5;
        servo.setTargetDeg(servoMin);
      }elif(inData.startsWith("relay")) {
        int num = inData.substring(5).toInt();
        pulse(num);
      }elif(inData.startsWith("on")) {
        int num = inData.substring(2).toInt();
        setPins(num, true);
      }elif(inData.startsWith("off")) {
        int num = inData.substring(3).toInt();
        setPins(num, false);
      }elif(inData.startsWith("ch")) {
        int num = inData.substring(2).toInt();
        setPins(num, !pin_state[num]);
      }elif(inData.startsWith("agel:")) {
        int num = inData.substring(5).toInt();
        servo.setTargetDeg(num);
      }elif(inData.startsWith("color:")) {
        int num = inData.substring(6).toInt();
        colors[2] = num;
      }elif(inData.startsWith("run:")) {
        is_run = inData.substring(4).toInt();
        Serial.print("is run = ");
        Serial.println(is_run);
      }

      inData = ""; // Clear recieved buffer
    }
    else {
      inData += recieved;
    }
  }
}

// -------------------     L O O P    -------------------------
void loop() {
  readSerial();
  WS_GO();
  if (is_run) update_btn();
  servo.tick();
}
