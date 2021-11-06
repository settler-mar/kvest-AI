#include <Arduino.h>

#define UART_S Serial
#define pinID 10 // пин определяющий ID
#define NAME "gloves"
String inData;
byte devId;

uint8_t outPin[] = { 12, 13,A0,A1 };
bool pin_state[] = { false, false };
#define out_cnt 2

#define btnCnt 1
uint8_t btnPin[] = { 2,3,4,5,6,7,8,9 };
boolean btnState[btnCnt];
unsigned long btnUndr[btnCnt]; // андребизг для отправки сообщений
unsigned long btnTimout = 0;
byte prevBtn = 255;
#define send_timeout 2000
#define Undr_time 100

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
  pinMode(pinID, INPUT);
  for (byte i = 0; i < out_cnt; i++)
  {
    pinMode(outPin[i], OUTPUT);
  }
  for (byte i = 0;i < btnCnt;i++) {
    pinMode(btnPin[i], INPUT);
    btnState[i] = false;
    btnUndr[i] = 0;
  }
  delay(300);
  devId = digitalRead(pinID) ? 1 : 0;

  reset();
  UART_S.println("init");
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
  delay(10);
}