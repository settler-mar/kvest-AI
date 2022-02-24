//#include "EasyNextionLibrary.h"  // Include EasyNextionLibrary
#include <FS.h>                   //this needs to be first, or it all crashes and burns...

#include <DNSServer.h>
#include <ESP8266WebServer.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
//#include <ESP8266HTTPClient.h>
#include <ArduinoHttpClient.h>

#include <nextioon.h>
// #define debug_game 1

#define client_finish client.stop();
#define SEND_BY_X_COMMAND

ESP8266WiFiMulti WiFiMulti;

String inData;
#define host "192.168.0.100"
#define httpPort 8080
#define SSID "ai"
#define WIFI_PASS "66430346"


// Define timeout time in milliseconds (example: 2000ms = 2s)
#define  timeoutTime 3000

String name = "hackDevice";
byte lg = 0;

#ifdef debug_game
  boolean start_game = true; //Обовленно ли имя
  bool has_lang = true;
  byte game = debug_game;
#else
  boolean start_game = false; //Обовленно ли имя
  bool has_lang = false;
  byte game = 0;
#endif

// Current time
unsigned long currentTime = millis();
// Previous time
unsigned long previousTime = 500;
unsigned long previousTime2 = 500;
unsigned long serial_t = millis();

WiFiServer server(80);

void send(String);
void updateLg();

//игры
#include "air.h"
#include "codes.h"
#include "gloves.h"


void updateLg() { // отправить на дисплей язык
  if (not start_game) return;
  myNextion_cr();
  if (game == 1) {
    myNex_writeNum("air.pic", lg);
    myNex_writeNum("air.air.pic", lg);
  }
}

bool test_get_lang(String currentLine) {
  int j = currentLine.indexOf("GET /lang/");
  if (j >= 0) {
    String lang = currentLine.substring(j + 10, j + 12);
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
  int j = currentLine.indexOf("GET /game/");
  if (j >= 0) {
    game = currentLine.substring(j + 10, j + 11).toInt();
    myNex_writeNum("n0.val", game);
    return true;
  }
  return false;
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
      if (client.available()) {             // if there's bytes to read from the client,
        currentLine = client.readStringUntil('\n');
        if (currentLine.length() > 0 and currentLine.indexOf("GET") >= 0) {
          if (test_get_lang(currentLine) ||
            (not start_game && test_get_game(currentLine)) ||
            ((game == 1) && getAir(currentLine)) ||
            ((game == 3) && getGloves(currentLine))
            ) {
            client.flush();
            client.println("ok");
            client_finish
              return;
          }
          client.println("wr");
          client_finish
            return;
        }
      }
    }
    client.flush();
    client.println("ok");
    client_finish
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

void processed_serial() {
  if (inData.length() > 2) {
    if (game == 1 && inData.charAt(0) == 0x23) serialAir(inData);
    if (game == 2 && inData.charAt(0) == 0x02) serialCodes(inData);
    if (game == 3 && inData.charAt(0) == 0x03) serialGloves(inData);
  }
  inData = ""; // Clear recieved buffer
  serial_t = 0;
}

void readSerial() {
  while (Serial.available() > 0)
  {
    serial_t = millis();
    char recieved = Serial.read();
    if (recieved == '\n')
    {
      processed_serial();
    }
    else {
      if (recieved == 0xff) {
        byte l = inData.length();
        if (l > 3 && inData.charAt(l - 1) == 0xff && inData.charAt(l - 2) == 0xff) {
          inData = "";
          return;
        }
      }
      inData += recieved;
    }
  }
  if (serial_t && serial_t + 150 < millis()) {
    processed_serial();
  }
}

void setup() {
  Serial.begin(9600);
  Serial.println();
  Serial.println("start");

  /*SPIFFS.begin();
  delay(600);
  SPIFFSConfig cfg;
  cfg.setAutoFormat(true);
  SPIFFS.setConfig(cfg);*/

  WiFi.setSleepMode(WIFI_NONE_SLEEP);
  WiFi.begin(SSID, WIFI_PASS);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println();
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  myNextion_cr();

  server.begin();
}

void loop() {
  // Serial.println(0);
  if (not start_game) {
    if (previousTime2 < millis()) {
      previousTime2 = millis() + 1000;
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
  if (game == 1) {
    checkResultAir();
  }
  // Serial.println(4);
  delay(10);
}
