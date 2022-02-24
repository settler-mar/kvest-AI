#include <Arduino.h>
#include <EEPROM.h>


#define UART_S Serial
#define NAME "gloves"
String inData;
#define devId EEPROM.read(0)

#define fbPin 13
unsigned long dg_timer = 0;
#define dg_timout 50

uint8_t outPin[] = { A0, 11, 12 };
bool pin_state[] = { false, false };
#define out_cnt 4

#define btnCnt 8
uint8_t btnPin[] = { 2,3,4,5,6,7,8,9 };
boolean btnState[btnCnt];
unsigned long btnUndr[btnCnt]; // андребизг для отправки сообщений
unsigned long btnTimout = 0;
byte prevBtn = 255;
#define send_timeout 2000
#define Undr_time 50

void setPins(byte pin, boolean stat) {
  pin_state[pin] = stat;
  digitalWrite(outPin[pin], stat ? LOW : HIGH);
  Serial.print("digital");
  Serial.print(pin);
  Serial.print(":");
  Serial.println(stat ? 1 : 0);
}

void  checkInput() {
  byte led = false;
  for (byte i = 0;i < btnCnt;i++) {
    byte st = !digitalRead(btnPin[i]);
    led = led || !st;
    if (btnState[i] != st and btnUndr[i] < millis()) {
      btnUndr[i] = millis() + Undr_time;
      if (st) {
        if (prevBtn != i or millis() > btnTimout) {
          prevBtn = i;
          Serial.print("btn:");
          Serial.print(devId);
          Serial.println(i);
          digitalWrite(fbPin, HIGH);
          dg_timer = millis() + dg_timout;
        }
        btnTimout = millis() + send_timeout;
      }
      btnState[i] = st;
    }
  }
}

void reset() {
  for (byte i = 0; i < out_cnt; i++)
  {
    setPins(i, false);
  }
}

void setup() {
  UART_S.begin(9600);
  UART_S.println("load");
  delay(300);
  Serial.print("dev id ");
  Serial.println(devId);

  for (byte i = 0; i < out_cnt; i++)
  {
    pinMode(outPin[i], OUTPUT);
  }
  pinMode(fbPin, OUTPUT);
  digitalWrite(fbPin, LOW);
  for (byte i = 0;i < btnCnt;i++) {
    pinMode(btnPin[i], INPUT);
    btnState[i] = false;
    btnUndr[i] = 0;
  }
  reset();
  UART_S.print("init: ");
  UART_S.println(devId);
}

void readSerial() {
  if (UART_S.available() > 0)
  {
    char recieved = UART_S.read();
    if (recieved == '\n')
    {
      if (inData.startsWith("name")) {
        UART_S.print("name:");
        UART_S.print(NAME);
        UART_S.println(devId);
      }
      else if (inData.startsWith("reset")) {
        reset();
        // Serial.println(">reset");
      }
      /*else if (inData.startsWith("open")) {
        int num = inData.substring(4).toInt();
        moveMotor(num, true);
        // Serial.print(">open");
        // Serial.println(num);
      }
      else if (inData.startsWith("close")) {
        int num = inData.substring(5).toInt();
        moveMotor(num, false);
        // Serial.print(">close");
        // Serial.println(num);
      }*/
      else if (inData.startsWith("on")) {
        int num = inData.substring(2).toInt();
        setPins(num, true);
      }
      else if (inData.startsWith("off")) {
        int num = inData.substring(3).toInt();
        setPins(num, false);
      }
      else if (inData.startsWith("ch")) {
        int num = inData.substring(2).toInt();
        setPins(num, !pin_state[num]);
      }
      else if (inData.startsWith("dev_id")) {
        EEPROM.write(0, inData.substring(6).toInt());
        Serial.print("Set dev id: ");
        Serial.println(EEPROM.read(0));
      }

      inData = ""; // Clear recieved buffer
    }
    else {
      inData += recieved;
    }
  }
}

void loop() {
  readSerial();
  checkInput();
  if (dg_timer and (dg_timer < millis())) {
    // Serial.print(dg_timer);
    // Serial.print(" ");
    // Serial.println(millis());
    digitalWrite(fbPin, LOW);
    dg_timer = 0;
  }
  delay(1);
}