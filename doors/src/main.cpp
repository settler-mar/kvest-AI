/*
  Алгоритм работы Двери
1. При включении – состояние дверей Открыто.
  Закрыть можно герконами или кнопкой.
2. При срабатывании геркона или кнопки –
   дверь открывается или закрывается в зависимости
   от сохранённого состояния двери.
3. При включении мотора двери включается звук и
    выводится на динамик соответствующей двери.
4. При нажатии на кнопку – включается светодиод.

Есть вариант Начало и завершение игры проводить
кнопкой "Старт/Сброс" на ЦП.

*/

/*
  v02

  1. Commented DFplayer
  2. Added UART CP commands
      get commands "DOOR"+num+">"
      sent commands "UNK" - Unknown if unknown door num
                    "DOOR"+num+"_OPEN>" if motor open
                    "DOOR1_ALREADY_OPENED>" if opened

  v03

  1. Added DFplayer 2 sounds (3 + 4)
  2. Checked serial signals
  3. Added DFplayer delay before startup
  4. If DOOR_X_> received & door is opened - don't move door

  v04

  1. play only one track 0001.mp3 and stop after motor stop
  2. different time for each motor
  3. short open Door1 after start

  v05
  Звук отключен
*/

#include <Arduino.h>

// -------------------        IO setup     -------------------------

uint8_t btnPin[] = { A0,A1,A2 };
#define LED A3

byte motorPin[][2] = { {13,12},{11,10},{8,9} }; // {close,open}
#define M1_FW 13
#define M1_BW 12
#define M2_FW 11
#define M2_BW 10
#define M3_FW 8
#define M3_BW 9

#define CP_RX 4
#define CP_TX 5

#define NOP __ams__("nop\n\t")

uint8_t outPin[] = { 7, 6 };
bool pin_state[] = { false, false };
#define out_cnt 2

// -------------------     C O N S T A N T S    -------------------------

#define TEST_TIME 1000  // time ms LED ON on startup
unsigned int moto_time[] = { 4000,8500,8000 }; //Задержка на движение дверей
unsigned int moto_time_max = 9000;

// Central Plate serial
#define UART_S Serial //интерфейс с WI-FI модулем
#define NAME "doors"
String inData;

// -------------------     V A R I A B L E S    -------------------------

// btns state
boolean btnState[] = { false,false,false };
unsigned long btnUndr[] = { 0,0,0 }; // андребизг для отправки сообщений
#define Undr_time 1000
boolean dState[] = { true,true,true };// doors state 



unsigned long timer[] = { 0,0,0 };
boolean door_moved = false;

byte is_run = 0; // запущенна ли игра 0-запущенно
// -------------------     F U N C T I O N S    -------------------------

void setPins(byte pin, boolean stat) {
  pin_state[pin] = stat;
  digitalWrite(outPin[pin], stat ? LOW : HIGH);
  Serial.print("digital");
  Serial.print(pin);
  Serial.print(":");
  Serial.println(stat ? 1 : 0);
}

void IOinitialOFF() {
  // HIGH on relay = OFF
  digitalWrite(M1_FW, HIGH);
  digitalWrite(M1_BW, HIGH);
  digitalWrite(M2_FW, HIGH);
  digitalWrite(M2_BW, HIGH);
  digitalWrite(M3_FW, HIGH);
  digitalWrite(M3_BW, HIGH);
}

void IOinit() {
  IOinitialOFF(); //Что б не дергнулись двери при включении

  for (byte i = 0; i < 3; i++)
  {
    pinMode(btnPin[i], INPUT);
  }

  pinMode(LED, OUTPUT);
  pinMode(M1_FW, OUTPUT);
  pinMode(M1_BW, OUTPUT);
  pinMode(M2_FW, OUTPUT);
  pinMode(M2_BW, OUTPUT);
  pinMode(M3_FW, OUTPUT);
  pinMode(M3_BW, OUTPUT);
  pinMode(outPin[0], OUTPUT);
  pinMode(outPin[1], OUTPUT);

  IOinitialOFF();
}


boolean btnCheck(byte pin) {
  if (!digitalRead(pin)) {
    return true;
  }
  return false;
}

void startTest() {

}

void moveMotor(byte motor, boolean stat) {
  // Serial.print("Start move ");
  // Serial.print(motor);
  // Serial.print(" ");
  // Serial.println(stat ? "open" : "close");

  if (dState[motor] == stat or timer[motor] > 0) {
    // Serial.println(dState[motor] == stat ? "not_ch" : "ch");
    // Serial.println(timer[motor]);
    return;
  }
  dState[motor] = stat;
  timer[motor] = millis();
  digitalWrite(motorPin[motor][stat ? 1 : 0], LOW);
  digitalWrite(motorPin[motor][stat ? 0 : 1], HIGH);
  door_moved = true;

  Serial.print("door");
  Serial.print(motor);
  Serial.println(":2");
  // Serial.println("GO");
}


void  checkInput() {
  byte led = false;
  for (byte i = 0;i < 3;i++) {
    byte st = digitalRead(btnPin[i]);
    led = led || !st;
    if (btnState[i] != st and btnUndr[i] < millis()) {
      btnUndr[i] = millis() + Undr_time;
      if (st) {
        if (i == 0) {
          moveMotor(0, !dState[0]);
        }
        if (i == 1) {
          Serial.println("reset_game");
        }
        if (i == 2) {
          moveMotor(1, !dState[1]);
          moveMotor(2, dState[1]);
          Serial.println("prestart_game");
        }
      }
      btnState[i] = st;
    }
  }
  if (led)
    digitalWrite(LED, LOW);
  else
    digitalWrite(LED, HIGH);
}

void doorProcessed() {
  if (!door_moved) return;
  door_moved = false;
  for (byte i = 0;i < 3;i++) {
    if (timer[i] > 0) {
      if (millis() - timer[i] < moto_time[i]) {
        door_moved = true;
      }
      else
      {
        Serial.print("door");
        Serial.print(i);
        Serial.print(":");
        Serial.println(dState[i] ? "1" : "0");
        if (i == 0 && !dState[i] && is_run) {
          is_run -= 1;
          if (is_run == 0) {
            Serial.println("start_game");
          }else{
            for (byte i = 0; i < 3; i++)
            {
              moveMotor(i, false); // close doors
            }
          }
        }
        timer[i] = 0;
        digitalWrite(motorPin[i][0], HIGH);
        digitalWrite(motorPin[i][1], HIGH);
      }
    }
  }
  if (!door_moved) {
    IOinitialOFF();
  }
}

void startMotors() {
  for (byte i = 0;i < 3;i++) {
    if (btnState[i]) {
      if (i == 0) {
        moveMotor(0, !dState[0]);
      }
      if (i == 1) {
        Serial.println("reset_game");
      }
      if (i == 2) {
        moveMotor(1, !dState[1]);
        moveMotor(2, dState[1]);
      }
    }
  }
}

void reset() {
  for (byte i = 0; i < 3; i++)
  {
    moveMotor(i, true); // open doors
  }
  for (byte i = 0; i < out_cnt; i++)
  {
    setPins(i, false);
  }
  is_run = 2;
}

// -------------------     S E T U P    -------------------------

void setup() {

  IOinit();

  UART_S.begin(9600);
  UART_S.println("load");
  startTest();
  reset();
  delay(moto_time_max);
  moveMotor(0, true); // open door0
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
        UART_S.println(NAME);
      }
      else if (inData.startsWith("reset")) {
        reset();
        // Serial.println(">reset");
      }
      else if (inData.startsWith("open")) {
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
      }
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

// -------------------     L O O P    -------------------------

void loop() {
  checkInput();
  readSerial();
  doorProcessed();
}
