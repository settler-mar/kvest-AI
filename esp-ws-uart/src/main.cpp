#include <FS.h>                   //this needs to be first, or it all crashes and burns...

#include <DNSServer.h>
#include <ESP8266WebServer.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
//#include <ESP8266HTTPClient.h>
#include <ArduinoHttpClient.h>

#include "FS.h" // SPIFFS is declared

ESP8266WiFiMulti WiFiMulti;

String inData;
#define host "192.168.0.114"
#define httpPort 3000
#define SSID "Settler-test"
#define WIFI_PASS "12346579"

String name = "start";
boolean set_name = false; //Обовленно ли имя

// Define timeout time in milliseconds (example: 2000ms = 2s)
#define  timeoutTime 3000

// Current time
unsigned long currentTime = millis();
// Previous time
unsigned long previousTime = 0; 

WiFiServer server(80);



void get(){
  WiFiClient client = server.available();   // Listen for incoming clients

  if (client) {                             // If a new client connects,
    //Serial.println("New Client inner.");          // print a message out in the serial port
    String currentLine = "";                // make a String to hold incoming data from the client
    currentTime = millis();
    previousTime = currentTime;
    while (client.connected() && currentTime - previousTime <= timeoutTime) { // loop while the client's connected
      currentTime = millis();         
      if (client.available()) {             // if there's bytes to read from the client,
        char c = client.read();             // read a byte, then
        if (c == '\n') {                    // if the byte is a newline character
          if (currentLine.length() > 0 and currentLine.indexOf("GET")>=0) {
            if (currentLine.indexOf("GET /getName") >= 0) {
              Serial.println("name");
              client.println("ok");
              client.stop();
              return;
            }else{
              int st = currentLine.indexOf("GET /")+5;
              int en = currentLine.indexOf(" ", st+1);
              if(en>0){
                Serial.println(currentLine.substring(st,en));  
              }else{
                Serial.println(currentLine.substring(st));
              }
            }
          }
          client.readString();     
        } else if (c != '\r') {  // if you got anything else but a carriage return character,
          currentLine += c;      // add it to the end of the currentLine
        }
      }
    }
    client.println("ok");
    client.stop();
    //Serial.println("Client disconnected.");
    //Serial.println("");
  }
}
/*
void send(String url_ = ""){
  HTTPClient http;
  WiFiClient client;

  String url="/esp/";
  url.concat(name);
  if(url_!=""){
    url.concat("/");
    url.concat(url_);
  }

  char url2[url.length()];
  url.toCharArray(url2, url.length());

  http.setTimeout(timeoutTime);

  http.begin(client, host,httpPort,url2);

  Serial.println(url);
  int httpCode = http.GET();
  
  if(httpCode > 0) {
    Serial.println(httpCode);
    //if(httpCode == HTTP_CODE_OK) {
    //  http.writeToStream(&Serial);
    //}
  }else{
    Serial.println(url);
    Serial.print("HTTP Conect to ");
    Serial.print(host);
    Serial.print(":");
    Serial.print(httpPort);
    Serial.println(" failed");
  }
  http.end();
  client.stop();
}/**/

void send(String url_ = ""){
  WiFiClient wifi;
  HttpClient client = HttpClient(wifi, host, httpPort);

  String url="/esp/"+name;
  
  char url2[url.length()+1];
  url.toCharArray(url2, url.length());

  //Serial.println(url2);

  client.beginRequest();
  client.get(url2);
  client.sendHeader("X-COMMAND", url_);
  client.endRequest();
}/**/
/*
void send(String url = ""){
  WiFiClient client;

  if (!client.connect(host, httpPort)) {
    Serial.print("Coonect to ");
    Serial.print(host);
    Serial.print(":");
    Serial.print(httpPort);
    Serial.println(" failed");
    return;
  }
  //Serial.print("Requesting URL: ");
  //Serial.println(url); // This will send the request to the server
  if (url != "") {
    url = "/" + url;
  }

  url="/esp/"+ name + url;

  String req = String("GET ") + url + " HTTP/1.0\r\n" + 
   "Host: " + host + ":" + String(httpPort) + "\r\n" +
   "User-Agent: ESP01\r\n" +
   "Connection: close\r\n" +
   "\r\n";

  char req_[req.length()];
  req.toCharArray(req_, req.length());
  client.print(req_);
  Serial.println(req_);
    //client.print("GET "+url+" HTTP/1.1\n");
    //client.print("Host: " + String(host) + ":" + String(httpPort) + "\n");
    //client.print("Connection: close\n\n\n");

  unsigned long timeout = millis();
  while (client.available() == 0) {
    if (millis() - timeout > timeoutTime){ 
      Serial.println(">>> Client Timeout !");
      client.stop();
      return;
    }
  } 
  
  // Read all the lines of the reply from server and print them to Serial
  while (client.available())
  { 
    String line = client.readStringUntil('\r'); Serial.println(line);
    client.readString();
  }
  //Serial.println();
  //Serial.println("closing connection"); 
  client.stop();
}/**/


void setup() {
	Serial.begin(9600);

  SPIFFS.begin();
  delay(600);
  SPIFFSConfig cfg;
  cfg.setAutoFormat(true);
  SPIFFS.setConfig(cfg);

  File f = SPIFFS.open("/f.txt", "r");
  if (f) {
    name = f.readString();
    f.close();
  }

	//Serial.setDebugOutput(true);
	Serial.setDebugOutput(false);

	Serial.println();
	Serial.println();
	Serial.println();

  WiFiMulti.addAP(SSID, WIFI_PASS);

  Serial.print("[SETUP] WIFI connect");
	while(WiFiMulti.run() != WL_CONNECTED) {
    Serial.print(".");
		delay(100);
	}
  Serial.println("OK");

  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  server.begin();
  Serial.println("[SETUP] Init finish");
  Serial.println();
}

void readSerial(){
    if (Serial.available() > 0)
    {
        char recieved = Serial.read();
        if (recieved == '\n')
        {
          if(inData.startsWith("name:")){
            name = inData.substring(5);
            if(name.length()>5){
              set_name = true;
              File configFile = SPIFFS.open("/f.txt", "w");
              configFile.print(name);
              configFile.close();

              send();
            }
          }else{
            send(inData);
          }

          //Serial.print("Arduino Received: ");
          //Serial.println(inData);
          inData = ""; // Clear recieved buffer
        }else{
          inData += recieved; 
        }
    }
}

void loop() {
  if(not set_name){
    if((millis() % 5000 == 0) && (previousTime < millis())){
      previousTime = millis()+1000;
      Serial.println("name");
    }
  }
	readSerial();
  get();
}