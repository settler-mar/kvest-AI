#include <DFRobotDFPlayerMini.h>
#include <SoftwareSerial.h>

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
*/



// -------------------        IO setup     -------------------------

#define BTN1 A0
#define GK2 A1
#define GK3 A2
#define LED A3
#define MP3_RX A4 // could be problem with RX
#define MP3_TX A5 // could be problem with RX


#define M1_FW 13
#define M1_BW 12
#define M2_FW 11
#define M2_BW 10
#define M3_FW 8
#define M3_BW 9
#define SND2  6
#define SND3  7
#define CP_RX 4
#define CP_TX 5

#define NOP __ams__("nop\n\t")

// -------------------     C O N S T A N T S    -------------------------

#define TEST_TIME 1000  // time ms LED ON on startup
#define NOISE_DELAY 25  // debounce delay
#define MOTOR1_ON_TIME 4000  // time while motor is ON
#define MOTOR2_ON_TIME 8500  // time while motor is ON
#define MOTOR3_ON_TIME 8000  // time while motor is ON
#define MOTOR4_ON_TIME 2000  // short open Door1 after start


// -------------------     DFplayer setup   -------------------------

DFRobotDFPlayerMini myDFPlayer;
SoftwareSerial playerSerial(MP3_RX, MP3_TX); // RX, TX

// Central Plate serial
SoftwareSerial cpSerial(CP_RX, CP_TX); // RX, TX


// -------------------     V A R I A B L E S    -------------------------

// btns state
boolean btn1State = false;  
boolean gk2State = false;
boolean gk3State = false;
// doors state 
boolean d1Open = true;  
boolean d2Open = true;
boolean d3Open = true;
unsigned long timer = 0;

// -------------------     F U N C T I O N S    -------------------------

void IOinit(){
    /*
 * без строки "digitalWrite(M1_FW, HIGH);" перед "pinMode" при включении
 * ардуины будет происходить кратковременное переключение реле,
 * а значит кратковременно подастся питание, что нам категорически
 * не надо!
 */
  digitalWrite(M1_FW, HIGH);

    pinMode(BTN1, INPUT);
    pinMode(GK2, INPUT);
    pinMode(GK3, INPUT);
    
    pinMode(LED, OUTPUT);
    pinMode(M1_FW, OUTPUT);
    pinMode(M1_BW, OUTPUT);
    pinMode(M2_FW, OUTPUT);
    pinMode(M2_BW, OUTPUT);
    pinMode(M3_FW, OUTPUT);
    pinMode(M3_BW, OUTPUT);
    pinMode(SND2, OUTPUT);
    pinMode(SND3, OUTPUT);
    

    IOinitialState();
}

void IOinitialState(){
  

    digitalWrite(LED, HIGH);
    // HIGH on relay = OFF
    digitalWrite(M1_FW, HIGH);
    digitalWrite(M1_BW, HIGH);
    digitalWrite(M2_FW, HIGH);
    digitalWrite(M2_BW, HIGH);
    digitalWrite(M3_FW, HIGH);
    digitalWrite(M3_BW, HIGH);
    digitalWrite(SND2, HIGH);
    digitalWrite(SND3, HIGH);
}

// DF_Player init
void init_Player(){
    playerSerial.begin(9600);
    delay(10); // added in last version to disable uninitialized Player
    Serial.println();
    Serial.println(F("Initializing DFPlayer ... (May take 3~5 seconds)"));
    // if not initialized - check power & signal cables
    if (!myDFPlayer.begin(playerSerial)) {
      Serial.println(F("Unable to begin:"));
      Serial.println(F("1.Please recheck the connection!"));
      Serial.println(F("2.Please insert the SD card!"));
      while(true){
        flash();
      };
    }
    Serial.println(F("DFPlayer Mini online."));
    myDFPlayer.volume(25);  //Set volume value. From 0 to 30
}

// blink LED
// ++
void flash()
{
    digitalWrite(LED, LOW);
    delay(300);
    digitalWrite(LED, HIGH);
    delay(300);
}

boolean pinPushed(byte pin){
  if(!digitalRead(pin)){
      delay(NOISE_DELAY);
      if(!digitalRead(pin))
          return true;
  }
  return false;
}

void startTest(){
  timer = millis();
  digitalWrite(LED, LOW);
  while(millis()-timer < TEST_TIME){
      delay(50);
  }
  digitalWrite(LED, HIGH);
  timer = 0;
}

void  checkInput(){
    btn1State = false;  
    gk2State = false;
    gk3State = false;
    if(pinPushed(BTN1)){
        btn1State = true;
        return;
    }
    if(pinPushed(GK2)){
        gk2State = true;
        return;
    }
    if(pinPushed(GK3)){
        gk3State = true;
        return;
    }
    
}
  
void  checkSerial(){
  // when you want to listen on a port, explicitly select it:
  cpSerial.listen();
  if (cpSerial.available()){
      String val = "";
        // read as string removes 'я' error chars from string
        // read string for End symbol
        val.concat(cpSerial.readStringUntil('>'));
        // read string for timeout
//        com.concat(cpSerial.readStringUntil('!'));

      delay(1); // wait 9 symbols received
      cpSerial.flush(); // delete all received data in serial
      
      if(val=="")
         return;
      
       // get command
      int start = val.indexOf("DOOR");
      if(start<0 || start>3)
        return;
     
      // get DOOR number
      int num = val.substring(start+4).toInt();
      switch(num){
        case 1: if(!d1Open){
                    btn1State = true;
                    cpSerial.print("DOOR1_OPEN>");
                } else {
                    cpSerial.print("DOOR1_ALREADY_OPENED>");
                }
          break;
        case 2: if(!d2Open){
                    gk2State = true;
                    cpSerial.print("DOOR2_OPEN>");
                } else {
                    cpSerial.print("DOOR2_ALREADY_OPENED>");
                }
          break;
        case 3: if(!d3Open){
                    gk3State = true;
                    cpSerial.print("DOOR3_OPEN>");
                } else {
                    cpSerial.print("DOOR3_ALREADY_OPENED>");
                }
          break;
        default:cpSerial.print("UNK>");
      }
      
    }
}

void playSnd() {
    if(btn1State){
        digitalWrite(SND2, HIGH);
        digitalWrite(SND3, HIGH);
    } else {
      if(gk2State){
          digitalWrite(SND2, LOW);
          digitalWrite(SND3, HIGH);
      } else if(gk3State){
          digitalWrite(SND2, LOW);
          digitalWrite(SND3, LOW);
      }
    }
    playTrack(1); // play move SND
}

void printDetail(uint8_t type, int value){
  switch (type) {
    case TimeOut:
      Serial.println(F("Time Out!"));
      break;
    case WrongStack:
      Serial.println(F("Stack Wrong!"));
      break;
    case DFPlayerCardInserted:
      Serial.println(F("Card Inserted!"));
      break;
    case DFPlayerCardRemoved:
      Serial.println(F("Card Removed!"));
      break;
    case DFPlayerCardOnline:
      Serial.println(F("Card Online!"));
      break;
    case DFPlayerPlayFinished:
      Serial.print(F("Number:"));
      Serial.print(value);
      Serial.println(F(" Play Finished!"));
      break;
    case DFPlayerError:
      Serial.print(F("DFPlayerError:"));
      switch (value) {
        case Busy:
          Serial.println(F("Card not found"));
          break;
        case Sleeping:
          Serial.println(F("Sleeping"));
          break;
        case SerialWrongStack:
          Serial.println(F("Get Wrong Stack"));
          break;
        case CheckSumNotMatch:
          Serial.println(F("Check Sum Not Match"));
          break;
        case FileIndexOut:
          Serial.println(F("File Index Out of Bound"));
          break;
        case FileMismatch:
          Serial.println(F("Cannot Find File"));
          break;
        case Advertise:
          Serial.println(F("In Advertise"));
          break;
        default:
          break;
      }
      break;
    default:
      break;
  }

}

void playTrack(int num) {
    playerSerial.listen();
    myDFPlayer.play(num); // play first track
//   myDFPlayer.playMp3Folder(1);  //Play the NUM mp3
   //play specific mp3 in SD:/MP3/0004.mp3; File Name(0~65535)
}

void moveMotor(byte motor, byte i){
      playSnd();
      timer = millis();
      digitalWrite(motor, LOW);
      unsigned long int MOTOR_ON_TIME = 7000;
      if (i == 1) MOTOR_ON_TIME = MOTOR1_ON_TIME;
      else if (i == 2) MOTOR_ON_TIME = MOTOR2_ON_TIME;
      else if (i == 3) MOTOR_ON_TIME = MOTOR3_ON_TIME;
      else if (i == 4) MOTOR_ON_TIME = MOTOR4_ON_TIME;
      while(millis()-timer < MOTOR_ON_TIME){
          checkInput();
          enlightLED();
      }
      myDFPlayer.stop();
//      playTrack(4); // play stop SND
      digitalWrite(motor, HIGH);
      timer = 0;
}
  
void startMotors(){
    if(btn1State){
      if(d1Open)
        moveMotor(M1_FW, 1);
      else
        moveMotor(M1_BW, 1);
      d1Open = !d1Open;
      return;
    }
    if(gk2State){
      if(d2Open)
        moveMotor(M2_FW, 2);
      else
        moveMotor(M2_BW, 2);
      d2Open = !d2Open;
      return;
    }
    if(gk3State){
      if(d3Open)
        moveMotor(M3_FW, 3);
      else
        moveMotor(M3_BW, 3);
      d3Open = !d3Open;
      return;
    }
}

void enlightLED(){
  if(btn1State || gk2State || gk3State)
    digitalWrite(LED, LOW);
  else
    digitalWrite(LED, HIGH);
}
  
  
  
// -------------------     S E T U P    -------------------------

void setup() {

    IOinit();

    Serial.begin(9600);
    
    cpSerial.setTimeout(100); // set wait timeout for string receive
    cpSerial.begin(9600);
    
    init_Player();
    
    
    startTest();
    moveMotor(M1_BW, 4); // open door1
}

// -------------------     L O O P    -------------------------

void loop() {
  checkInput();
  checkSerial();
  enlightLED();
  startMotors();
  
  // when you want to listen on a port, explicitly select it
//  playerSerial.listen();
//  if (myDFPlayer.available()) {
//    printDetail(myDFPlayer.readType(), myDFPlayer.read()); //Print the detail message from DFPlayer to handle different errors and states.
//  }
}
