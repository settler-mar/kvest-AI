#include <Arduino.h>
#include <FastLED.h>

// -------------------        IO setup     -------------------------

uint8_t btnPin[] = { A0,A1,A2,A3 };
#define btn_cnt 4

uint8_t relay[] = { 6,7 };
byte relayON[] = { 0,0 };
#define relay_cnt 2
#define relay_delay 500

uint8_t outPin[] = { 8, 9 };
bool pin_state[] = { false, false };
#define out_cnt 2
// -------------------     C O N S T A N T S    -------------------------

#define LED_PIN     5
#define COLOR_ORDER GRB
#define CHIPSET     WS2811
#define NUM_LEDS    btn_cnt*3
#define BRIGHTNESS  200

// Central Plate serial
#define NAME "air"
String inData;

#define elif else if

// -------------------     V A R I A B L E S    -------------------------

byte btnState[] = { 255,255,255,255 };
CRGB leds[NUM_LEDS];
bool is_run = false;

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

void send_status() {
  Serial.print("st:");
  for (byte i = 0;i < btn_cnt;i++) {
    Serial.print(btnState[i]);
  }
  Serial.println();
}

void setPins(byte pin, boolean stat) {
  pin_state[pin] = stat;
  digitalWrite(outPin[pin], stat ? LOW : HIGH);
  Serial.print("digital");
  Serial.print(pin);
  Serial.print(":");
  Serial.println(stat ? 1 : 0);
}


void update_leds(byte i, byte st) {
  leds[i * 3 + 2] = st == 0 && is_run ? CRGB(0, 0, 255) : CRGB::Black;
  leds[i * 3 + 1] = st == 1 && is_run ? CRGB(0, 0, 200) : CRGB::Black;
  leds[i * 3 + 0] = st == 2 && is_run ? CRGB(0, 0, 255) : CRGB::Black;
}

void update_btn() {
  bool has_upd = false;
  for (byte i = 0;i < btn_cnt;i++) {
    byte st = convertA2Pos(btnPin[i]);
    delay(10);
    if (btnState[i] != st) {
      has_upd = true;
      btnState[i] = st;
      update_leds(i, st);
    }
  }
  if (has_upd) {
    FastLED.show();
    send_status();
  }
}

void setup() {
  Serial.begin(9600);
  delay(500);
  FastLED.addLeds<CHIPSET, LED_PIN, COLOR_ORDER>(leds, NUM_LEDS).setCorrection(TypicalLEDStrip);
  FastLED.setBrightness(255);
  for (byte i = 0;i < NUM_LEDS;i++) {
    leds[i] = 0xFFFFFF;
  }
  FastLED.show();
  delay(1000);
  FastLED.clear();
  FastLED.show();

  for (byte i = 0;i < relay_cnt;i++) {
    pinMode(relay[i], OUTPUT);
    digitalWrite(relay[i], not relayON[i]);
  }

  for (byte i = 0;i < out_cnt;i++) {
    pinMode(outPin[i], OUTPUT);
    setPins(i, false);
  }

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
        is_run = false;
        FastLED.setBrightness(0);
        FastLED.clear();
        FastLED.show();
        for (byte i = 0;i < out_cnt;i++) {
          setPins(i, false);
        }
      }elif(inData.startsWith("start")) {
        pulse(0);
        FastLED.setBrightness(BRIGHTNESS);
        for (byte i = 0;i < btn_cnt;i++) {
          btnState[i] = 255;
        }
        is_run = true;
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
  if (is_run) update_btn();
}
