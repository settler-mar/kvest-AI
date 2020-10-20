#include <FS.h>                   //this needs to be first, or it all crashes and burns...

#include <DNSServer.h>
#include <ESP8266WebServer.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>


ESP8266WiFiMulti WiFiMulti;

String inData;
#define host "192.168.0.104"
#define httpPort 12345
String name = "start";
// Define timeout time in milliseconds (example: 2000ms = 2s)
#define  timeoutTime 2000

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
              Serial.println("getName");
              client.println("ok");
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

  /* url += "?param1=";
  url += param1;
  url += "?param2=";
  url += param2;
  */

void send(String url = "/"){
  WiFiClient client;

  if (!client.connect(host, httpPort)) {
    Serial.println("connection failed");
    return;
  }
  //Serial.print("Requesting URL: ");
  //Serial.println(url); // This will send the request to the server
  client.print(String("GET esp/") + name + "/" + url + " HTTP/1.1\r\n" + "Host: " + host + "\r\n" + "Connection: close\r\n\r\n");
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
    //String line = client.readStringUntil('\r'); Serial.print(line);
    client.readString();
  }
  //Serial.println();
  //Serial.println("closing connection"); 
  client.stop();
}

void setup() {
	Serial.begin(9600);

	//Serial.setDebugOutput(true);
	Serial.setDebugOutput(false);

	Serial.println();
	Serial.println();
	Serial.println();

	/*for(uint8_t t = 4; t > 0; t--) {
		Serial.printf("[SETUP] BOOT WAIT %d...\n", t);
		Serial.flush();
		delay(1000);
	}*/

  WiFiMulti.addAP("Settler-test", "12346579");

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
            send();
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
	readSerial();
  get();
}