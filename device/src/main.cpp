//#include "EasyNextionLibrary.h"  // Include EasyNextionLibrary
#include <FS.h>                   //this needs to be first, or it all crashes and burns...

#include <DNSServer.h>
#include <ESP8266WebServer.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
//#include <ESP8266HTTPClient.h>
#include <ArduinoHttpClient.h>

#include <nextioon.h>

#define client_finish client.stop();
#define SEND_BY_X_COMMAND

ESP8266WiFiMulti WiFiMulti;

String inData;
// #define host "192.168.0.225"
// #define httpPort 12345
// #define SSID "Settler-test"
// #define WIFI_PASS "12346579"
#define host "192.168.0.100"
#define httpPort 8080
#define SSID "ai"
#define WIFI_PASS "66430346"


// Define timeout time in milliseconds (example: 2000ms = 2s)
#define  timeoutTime 3000

String name = "hackDevice";
boolean start_game = false; //Обовленно ли имя

byte lg = 0;
bool has_lang = false;
byte game = 1;
// Current time
unsigned long currentTime = millis();
// Previous time
unsigned long previousTime = 500;
unsigned long previousTime2 = 500;

WiFiServer server(80);

void send(String);

// ввод кода
byte keys_map[] = { 0,1,2,3,4,5,6,7,8,9 }; // клавиатура. каждый раз перемешивается
byte keys_code[] = { 0,0,0,0 }; // верная комбинация
byte keys_code_read[] = { 0,0,0,0 }; // полученная комбинация
byte key_pos = 0; // текущий символ
byte pass_valid = 1;

//EasyNex myNex(Serial); // Create an object of EasyNex class with the name < myNex >

void updateCode() {
  key_pos = 0;
  pass_valid = 1;
  myNex_writeNum("n5.val", 9);//запуск таймера
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
    myNex_writeStr("t" + String(j) + ".txt", String(keys_map[j]));//передаем код
    myNex_writeNum("t" + String(j) + ".pco", 0);                  //сброс цвета
  }
  send(out);

  for (byte j = 0;j < 10;j++) {
    byte i = j + random(10 - j);
    byte c = keys_map[i];
    keys_map[i] = keys_map[j];
    keys_map[j] = c;
  }

  for (byte j = 0;j < 10;j++) {
    myNex_writeStr("b" + String(j) + ".txt", String(keys_map[j]));//передаем клавиши
  }
}

void updateLg() { // отправить на дисплей язык
  if (not start_game) return;
  Serial.print("\xFF\xFF\xFF");
  if (game == 1) {
    myNex_writeNum("air.pic", lg);
    myNex_writeNum("air.air.pic", lg);
  }
}

byte air_pos[4];
String air_pos_st = "";
byte air_timer = 20;
unsigned long air_pr_time = 0
void updateAir(String st) {
  air_pos_st = st;
  for (byte n = 0;n < 4;n++) {
    String s = st.substring(n, n + 1);
    air_pos[n] = s == "0" ? 0 : s == "2" ? 2 : 1;

    // Serial.print(n);
    // Serial.print(" ");
    // Serial.println(air_pos[n]); 
  }
}
void sendAir() {
  if (not start_game) return;
  byte airDors[] = { 0,1,2,3,2,3,0,1 };
  Serial.print("\xFF\xFF\xFF");
  for (byte i = 2;i < 8;i++) {
    myNex_writeNum("p" + String(i) + ".pic", 3 + 3 * i + air_pos[airDors[i]]);
  }
}

void checkResultAir() {
  if (not start_game) return;
  if (air_pos_st != "2020") {
    air_pr_time = 0;
    return;
  }
  if (air_pr_time == 0) {
    air_pr_time == millis() + 1000;
  }
  else if (air_pr_time < millis()) {
    air_pr_time = 0;
    air_timer += 2;

    if (air_timer == 90) {
      myNex_command("vis p0,1");
      myNex_writeNum("p0.pic", 3 + lg);
    }else   if (air_timer >= 90) {
      myNex_writeNum("p0.pic", 5 + lg);
      send("finish_1");
    }
  }
}

void get() {
  WiFiClient client = server.available();   // Listen for incoming clients
  if (client) {                             // If a new client connects,
    // Serial.println("New Client inner.");          // print a message out in the serial port
    String currentLine = "";                // make a String to hold incoming data from the client
    currentTime = millis();
    previousTime = currentTime;
    while (client.connected() && currentTime - previousTime <= timeoutTime) { // loop while the client's connected
      currentTime = millis();
      // Serial.println("while start."); 
      if (client.available()) {             // if there's bytes to read from the client,
        currentLine = client.readStringUntil('\n');
        //char c = client.read();             // read a byte, then
        //if (c == '\n') {                    // if the byte is a newline character
          // Serial.println(currentLine);
        if (currentLine.length() > 0 and currentLine.indexOf("GET") >= 0) {
          int j = currentLine.indexOf("GET /lang/");
          if (j >= 0) {
            String lang = currentLine.substring(j + 10, j + 12);
            // Serial.println();
            // Serial.println(lang);
            if (lang == "en") {
              client.println("ok");
              lg = 0;
              has_lang = true;
              updateLg();
            }
            else if (lang == "ru") {
              client.println("ok");
              lg = 1;
              has_lang = true;
              updateLg();
            }
            else if (lang == "ua") {
              lg = 2;
              client.println("ok");
              has_lang = true;
              updateLg();
            }
            else {
              client.println("err");
            }
            client_finish
              return;
          }
          j = currentLine.indexOf("GET /air:");
          if (j >= 0) {
            // Serial.println();
            // Serial.println(currentLine.substring(j+9,j+14));
            updateAir(currentLine.substring(j + 9, j + 14));
            sendAir();
            updateLg();
            checkResultAir();
            client.flush();
            client.println("ok");
            client_finish
              return;
          }
          /*else{
            int st = currentLine.indexOf("GET /")+5;
            int en = currentLine.indexOf(" ", st+1);
            if(en>0){
              Serial.println(currentLine.substring(st,en));
            }else{
              Serial.println(currentLine.substring(st));
            }
          }*/
          //client.println(myNex.currentPageId);
          client_finish
            return;
        }
      //} else if (c != '\r') {  // if you got anything else but a carriage return character,
      //  currentLine += c;      // add it to the end of the currentLine
      //}
      }
    }
    client.flush();
    client.println("ok");
    client_finish
    //Serial.println("Client disconnected.");
    //Serial.println("");
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

void send(String url_ = "") {
  WiFiClient wifi;
  HttpClient client = HttpClient(wifi, host, httpPort);

#ifdef SEND_BY_X_COMMAND
  String url = "/esp/" + name;
#else
  String url = "/esp/" + name;
  if (url_ != "") {
    url += "/" + url_;
  }
#endif

  byte url_len = url.length() + 1;
  char url2[url_len];
  url.toCharArray(url2, url_len);

  client.beginRequest();
  client.get(url2);
#ifdef SEND_BY_X_COMMAND
  if (url_ != "") {
    url_ = clearName(url_);
    url_len = url_.length() + 1;
    char url_2[url_len];
    url_.toCharArray(url_2, url_len);

    client.sendHeader("X-COMMAND", url_2);
    client.sendHeader("test", url_len);
    client.sendHeader("ZA", url2);
    // Serial.println(url_len);
  }
#endif
  client.endRequest();
}

void readSerial() {
  while (Serial.available() > 0)
  {
    char recieved = Serial.read();
    if (recieved == '\n')
    {
      if (game == 1) {
        if (inData.charAt(0) == 0x23 && inData.charAt(1) == 0x02 && inData.charAt(2) == 0x52) {
          start_game = true;
          sendAir();
        }
        // updateLg();
      }
      if (game == 2 and inData.charAt(0) == 0x02) {
        if (inData.charAt(1) == 0x01 && inData.charAt(2) == 0x00) {
          updateCode();
        }
        if (inData.charAt(1) == 0x00 && key_pos < 5) {
          keys_code_read[key_pos] = keys_map[inData.charAt(2)];
          // myNex_command("vis b"+String(int(inData.charAt(2)))+",0");
          myNex_writeNum("t" + String(key_pos) + ".pco", (keys_code_read[key_pos] == keys_code[key_pos]) ? 2016 : 63488);
          if (keys_code_read[key_pos] != keys_code[key_pos])pass_valid = 0;
          key_pos++;
          String out = "code_p:";
          for (byte j = 0;j < key_pos;j++) {
            out += String(keys_code_read[j]);
          }
          send(out);
          if (key_pos == 5 && pass_valid) {
            myNex_command("tm0.en=0");
            myNex_command("vis p0,1");
            send("finish_2");
          }
        }
      }
      inData = ""; // Clear recieved buffer
    }
    else {
      if (recieved == 0xff) {
        byte l = inData.length();
        if (inData.charAt(l - 1) == 0xff && inData.charAt(l - 2) == 0xff) {
          inData = "";
          return;
        }
      }
      inData += recieved;
    }
  }
}

void setup() {
  Serial.begin(9600);

  /*SPIFFS.begin();
  delay(600);
  SPIFFSConfig cfg;
  cfg.setAutoFormat(true);
  SPIFFS.setConfig(cfg);*/

  WiFi.setSleepMode(WIFI_NONE_SLEEP);
  WiFiMulti.addAP(SSID, WIFI_PASS);

  while (WiFiMulti.run() != WL_CONNECTED) {
    delay(100);
  }
  Serial.println();
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  server.begin();
}

void loop() {
  // Serial.println(0);
  if (not start_game) {
    if (previousTime2 < millis()) {
      previousTime2 = millis() + 1000;
      myNex_writeNum("n0.val", game);
    }
    //myNex.currentPageId
  }
  // Serial.println(1);
  readSerial();
  // Serial.println(2);
  get();
  // Serial.println(3);
  // Serial.println(previousTime);
  // Serial.println(millis());
  if (previousTime < millis()) {
    // Serial.print("n0.val=100");
    // Serial.write(0xff);Serial.write(0xff);Serial.write(0xff);
    if (has_lang) {
      send();
      previousTime = millis() + 10000;
    }
    else {
      send("lang");
      send("game");
      previousTime = millis() + 5000;
    }
  }
  // Serial.println(4);
  delay(10);
}
