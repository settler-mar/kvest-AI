//#include "EasyNextionLibrary.h"  // Include EasyNextionLibrary
#include <FS.h>                   //this needs to be first, or it all crashes and burns...

#include <SoftwareSerial.h>
#include <SPI.h>              // include libraries
#include <LoRa.h>

#define ss 15
#define rst 16
#define dio0 2

byte msgCount = 0;            // count of outgoing messages
byte localAddress = 0xBB;     // address of this device
byte destination = 0xFF;      // destination to send to
long lastSendTime = 0;        // last send time
int interval = 2000;          // interval between sends

SoftwareSerial dSerial; 
#include <dwin_diaplay.h>
// #define debug_game 2

#define client_finish client.stop();
#define SEND_BY_X_COMMAND

byte Buffer[20];                //Создать буфер
byte Buffer_Len = 0;
bool flag = false;

String name = "hackDevice";
byte lg = 0;
byte timer_to_game = 0;
uint32_t  myTimer;
boolean start_game = false; //запущенна ли игра

#ifdef debug_game
  bool has_lang = true;
  byte game = debug_game;
#else
  bool has_lang = false;
  byte game = 0;
#endif

// Current time
unsigned long currentTime = millis();
// Previous time
unsigned long previousTime = 500;
unsigned long serial_t = millis();

void send(String);
void updateLg();

//игры
#include "air.h"
#include "codes.h"
#include "gloves.h"
#include "satellite.h"


void updateLg() { // отправить на дисплей язык
  int_write(0x4000,lg);
}

bool test_get_lang(String currentLine) {
  int j = currentLine.indexOf("/lang/");
  if (j >= 0) {
    String lang = currentLine.substring(j + 6, j + 8);
    Serial.print("test_get_lang ");
    Serial.print(j);
    Serial.print(" ");
    Serial.print(currentLine.substring(j + 6, j + 8));
    Serial.print(" ");
    Serial.println(lang);

    if (lang == "en") {
      lg = 0;
      has_lang = true;
      updateLg();
    }
    else if (lang == "ru") {
      lg = 1;
      has_lang = true;
      updateLg();
    }
    else if (lang == "ua") {
      lg = 2;
      has_lang = true;
      updateLg();
    }
    return true;
  }
  return false;
}

bool test_get_game(String currentLine) {
  int j = currentLine.indexOf("/game/");
  if (j >= 0) {
    game = currentLine.substring(j + 6, j + 7).toInt();
    // myNex_writeNum("n0.val", game);
    return true;
  }
  return false;
}

void onReceive(int packetSize) {
  if (packetSize == 0) return;          // if there's no packet, return

  // read packet header bytes:
  // int recipient = LoRa.read();          // recipient address
  // byte sender = LoRa.read();            // sender address
  byte incomingMsgId = LoRa.read();     // incoming msg ID
  byte incomingLength = LoRa.read();    // incoming msg length

  String incoming = "";

  while (LoRa.available()) {
    incoming += (char)LoRa.read();
  }

  if (incomingLength != incoming.length()) {   // check length for error
    Serial.println("error: message length does not match length");
    return;                             // skip rest of function
  }

  // if the recipient isn't this device or broadcast,
  // if (recipient != localAddress && recipient != 0xFF) {
  //   Serial.println("This message is not for me.");
  //   return;                             // skip rest of function
  // }

  // if message is for this device, or broadcast, print details:
  // Serial.println("Received from: 0x" + String(sender, HEX));
  // Serial.println("Sent to: 0x" + String(recipient, HEX));
  // Serial.println("Message ID: " + String(incomingMsgId));
  // Serial.println("Message length: " + String(incomingLength));
  Serial.println("Message:" + incoming);
  Serial.println("RSSI:" + String(LoRa.packetRssi()));
  Serial.println("Snr:" + String(LoRa.packetSnr()));
  Serial.println();

  if (test_get_lang(incoming) ||
    (not start_game && test_get_game(incoming)) ||
    ((game == 1) && getAir(incoming)) ||
    ((game == 3) && getGloves(incoming))
    
    ) {
      return;
  }  
}

String clearName(String txt) {
  String out = "";
  for (byte i = 0; i < txt.length() + 1;i++) {
    if (txt.charAt(i) >= 0x30 and txt.charAt(i) <= 0x39) { // 0..9
      out += txt.charAt(i);
    }
    if (txt.charAt(i) >= 0x41 and txt.charAt(i) <= 0x5A) { //A-Z
      out += txt.charAt(i);
    }
    if (txt.charAt(i) >= 0x61 and txt.charAt(i) <= 0x7A) { //a-z
      out += txt.charAt(i);
    }
    if (txt.charAt(i) == 0x3A) { // :
      out += txt.charAt(i);
    }
    if (txt.charAt(i) == 0x5F) { // _
      out += txt.charAt(i);
    }
  }
  return out;
}

void send(String outgoing = "") {

  outgoing = clearName(outgoing);

  if (outgoing.length() < 2) return;
  LoRa.beginPacket();                   // start packet
  // LoRa.write(destination);              // add destination address
  // LoRa.write(localAddress);             // add sender address
  LoRa.write(msgCount);                 // add message ID
  LoRa.write(outgoing.length());        // add payload length
  LoRa.print(outgoing);                 // add payload
  LoRa.endPacket();                     // finish packet and send it
  msgCount++;                           // increment message ID
}

void processed_serial() {
  if (Buffer[0] == 0X5A && Buffer[1] == 0XA5) {
    if (!start_game){
      if (Buffer[4] == 0X50 && Buffer[5] == 0X70) {
        if (Buffer[7] == 0x21 && Buffer[8] == 0x31){
          timer_to_game = 50;
          start_game=false;
        }
      }
    }else if(game==1){
        // serialAir();
    }
    }else if(game==2){
        serialCodes();
    }else if(game==3){
        // serialGloves();
    }else if(game==4){
        serialSatellite();
    }

  if (Buffer[4] == 0X00) {  // Принимаем ситемные данные
    if (Buffer[5] == 0X82) {

    }
  }
  // if (inData.length() > 2) {
  //   if (game == 1 && inData.charAt(0) == 0x23) serialAir(inData);
  //   if (game == 2 && inData.charAt(0) == 0x02) serialCodes(inData);
  //   if (game == 3 && inData.charAt(0) == 0x03) serialGloves(inData);
  // }
  // inData = ""; // Clear recieved buffer
  // serial_t = 0;
}

void readSerial() {
  while (dSerial.available())
  {
    // go_to_page(3);
    serial_t = millis();
      Buffer[Buffer_Len] = dSerial.read();
      if (Buffer[Buffer_Len]<10) Serial.print(0);
      Serial.print(Buffer[Buffer_Len], HEX);
      Serial.print(" ");
      Buffer_Len++;
      flag = true;
    }
  if (flag)
    {
      processed_serial();
      Serial.println();
      Buffer_Len = 0; // сброс номера элемента в массиве
      flag = false;
    }
  // if (serial_t && serial_t + 150 < millis()) {
  //   processed_serial();
  // }
}

void mute(){
  byte mute_[]={0x5A, 0xA5, 0x07, 0x82, 0x00, 0x80, 0x5A, 0x00, 0x00, 0x30};
  dSerial.write(mute_, 10);
  delay(100);
}

void setup() {
  Serial.begin(115200);
  dSerial.begin(115200, SWSERIAL_8N1, 4, 5, false);

  LoRa.setPins(ss, rst, dio0);// set CS, reset, IRQ pin

  if (!LoRa.begin(433E6)) {             
    Serial.println("LoRa init failed. Check your connections.");
    while (true);                       // if failed, do nothing
  }

  // Serial.println();
  // Serial.println("start");
  /*delay(2000);
  go_to_page(15);
  while (true){
    for(byte i=0; i<10;i++){
      int_write(0x5001,i);
      for(byte j=0; j<10;j++){
        int_write(0x6000+j*16,i);
      }
      for(byte j=0; j<5;j++){
        int_write(0x6100+j*16,i);
        // int_write(0x6203+j*16,0xF800);
        int_write(0x6203+j*16,0x07E0);
      }
      delay(1000);
    }
  }/**/

  // SPIFFS.begin();
  // delay(600);
  // SPIFFSConfig cfg;
  // cfg.setAutoFormat(true);
  // SPIFFS.setConfig(cfg);

  delay(1000);
  // mute();
  go_to_page(0);
  updateLg();

  /*go_to_page(29);
  while (true){
    for (byte i=0;i<3;i++){
      lg=i;
      updateLg();
      // delay(2000);
      for (byte i=0;i<3;i++){
        int_write(0x5010+5, i*3+3);
        int_write(0x5010+6, i*3+5);
        Serial.println(i);
        // long_write(0x6314+i, 150+i*2);
        delay(1000);
      }
    }

    for (byte i=0;i<29;i++){
      int_write(0x5001, i);
      int_write(0x5002, i);
      int_write(0x5003, i);
      int_write(0x5004, i);
      int_write(0x5005, i);
      int_write(0x5006, i);
      Serial.println(i);
      // long_write(0x6314+i, 150+i*2);
      delay(100);
    }

    // checkResultAir();
    // readSerial();
    // onReceive(LoRa.parsePacket());
  }/**/
}

void loop() {
  // test_wifi();
  readSerial();
  onReceive(LoRa.parsePacket());
  if (previousTime < millis()) {
    // Serial.print("n0.val=100");
    // Serial.write(0xff);Serial.write(0xff);Serial.write(0xff);
    if (has_lang) {
      if (game==0){
        send("game");
        previousTime = millis() + 5000;
      }else{
        send("ping");
        previousTime = millis() + 10000;        
      }
    }
    else {
      send("lang");
      send("game");
      previousTime = millis() + 5000;
    }
  }

  if (myTimer<millis()){
    myTimer=millis()+100;
    if (timer_to_game){
      timer_to_game--;
      if (!timer_to_game){
        if (game){
          if (!start_game){
            start_game = true;
            if(game==1)go_to_page(26);
            if(game==2)updateCode();
            if(game==3)gloves_clear();
            if(game==4)go_to_page(30);
          }
        }else{
          timer_to_game = 20;
        }
      }
    }
    if (start_game){
      if (game == 1) checkResultAir();
      if (game == 2) codesLoop();
      if (game == 3) glovesLoop();
      if (game == 4) satelliteLoop();
    }
  }
}
