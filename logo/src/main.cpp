#include <Wire.h>
#include <SPI.h>
#include <Adafruit_CAP1188.h>
#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
#include <avr/power.h> // for NeoPixel
#endif

#define LOGO_OPEN        2  // открытие лого

// -------------------     CAP1188 setup   -------------------------

// Reset Pin is used for I2C or SPI
#define CAP1188_RESET  A0

// Use I2C, no reset pin!
//Adafruit_CAP1188 cap = Adafruit_CAP1188();

// Or...Use I2C, with reset pin (reset on .begin() function)
Adafruit_CAP1188 cap = Adafruit_CAP1188(CAP1188_RESET);

// -------------------     WS2812b setup   -------------------------

#define   LED_PIN        3  // выход на светодиоды

#define   STICK_NUM            6 //количество сборок
#define   PIXEL_IN_STICK       3 //светодиодов в сборке
#define   PIXEL_NUM            (STICK_NUM * PIXEL_IN_STICK)

Adafruit_NeoPixel leds = Adafruit_NeoPixel(PIXEL_NUM, LED_PIN, NEO_GRB + NEO_KHZ800);


// -------------------     V A R I A B L E S    -------------------------

const int startupDelay = 3000; //  delay before program start ms
boolean _loop = false; // finish flag
int lvl = 1; // game lvl
const int NOISE_DELAY = 25; // millis for debounce
const int DONE_DELAY = 3000; // millis for DONE signal
const int TEST_MINUTES = 2; // minutes for test
unsigned long timer = 0;

// -------      Capacitive Sensors variables   -------------

const int maxCapacitiveSensors = 6;         // sensors quantity <= 8
boolean buttonPushed[maxCapacitiveSensors]; // array of sensor state
int buttonCoolDownDelay = 500; // treshhold for increment to togggle sensor state

const int codeLength = 4; // must be <= maxCapacitiveSensors

// 9 5 0 7 4 2
//numbers on snake
const int nums[maxCapacitiveSensors] = { 9, 5, 0, 7, 4, 2 };
// code on snake
const int codeNums[codeLength] = { 0, 2, 5, 7 };
String enterCode = "";
// Sensor NUM from 1 to 8
int code[codeLength];
int input[codeLength];
int counter = 0;  // input code length counter

// Central Plate serial
#define UART_S Serial //интерфейс с WI-FI модулем
#define NAME "logo"
String inData;

void readSerial();
void capacitiveSensorsInit();
void setButtonColor(byte StickNum, uint32_t color);

// Fill the dots one after the other with a color
void colorWipe(uint32_t color, uint8_t wait = 0) {
  for (uint16_t i = 0; i < leds.numPixels(); i++) {
    leds.setPixelColor(i, color);
    leds.show();
    delay(wait);
  }
}

void ledsRed(void) {
  colorWipe(leds.Color(200, 0, 0));
}
void ledsGreen(void) {
  colorWipe(leds.Color(0, 200, 0));
}
void ledsBlue(void) {
  colorWipe(leds.Color(0, 0, 200));
}
void ledsOff(void) {
  colorWipe(leds.Color(0, 0, 0));
}

void startGame() {
    // reset capacitiveSensors;
  capacitiveSensorsInit();
  delay(50);
  ledsRed();
  enterCode = "";
  lvl = 2;
  counter = 0;
  Serial.println("start");
}


void setCode() {
  // Sensor NUM from 1 to 8
  // convert code on snake to sensors NUM code
  for (int j = 0; j < codeLength; j++) {
    for (int i = 0; i < maxCapacitiveSensors; i++) {
      enterCode += String(nums[i]);
      if (enterCode.length() > codeLength) {
        enterCode = enterCode.substring(1);
      }
      // UART_S.print("input:");
      // UART_S.println(enterCode);
      if (codeNums[j] == nums[i])
        code[j] = i + 1;
    }
  }
}

void capacitiveSensorsInit()
{
      // for 0x28 connect AD to 3V3
  if (!cap.begin(0x28)) {
  //  if (!cap.begin()) {
    UART_S.println("CAP1188 not found");
    while (1);
  }

  // Turn off multitouch so only one button pressed at a time
  cap.writeRegister(0x2A, 0x80);  // 0x2A default 0x80 use 0x41  — Set multiple touches back to off
  cap.writeRegister(0x41, 0x39);  // 0x41 default 0x39 use 0x41  — Set "speed up" setting back to off      
  cap.writeRegister(0x72, 0xff);  // 0x72 default 0x00  — Sets LED links back to off (default)
  cap.writeRegister(0x44, 0x41);  // 0x44 default 0x40 use 0x41  — Set interrupt on press but not release
  cap.writeRegister(0x28, 0x00);  // 0x28 default 0xFF use 0x00  — Turn off interrupt repeat on button hold

  // Sensitivity Control
  // sensitivity of the threshold and delta counts and data scaling of the base counts
  // default value 2Fh
  uint8_t reg = cap.readRegister(0x1f) & 0x0f;
  // cap.writeRegister(0x1f, reg | 0x5F); // 5F works fine
  cap.writeRegister(0x1f, 0x3F); // 5F works fine
  //Decrease sensitivity a little - default is 0x2F (32x) per datasheet
  //( 0x3F);  // 16x sensitivity
  //( 0x4F);  // 8x  sensitivity
  //( 0x5F);  // 4x  sensitivity
  //cap.writeRegister(0x6F);  // 2x  sensitivity THIS SEEMS TO WORK THE BEST FOR 3.5" plate sensors
  //cap.writeRegister( 0x7F);  // 1x  sensitivity

  // define all Sensors unpushed
  for (int i = 0;i < maxCapacitiveSensors;i++) {
    buttonPushed[i] = false;
  }
}

void startTest() {
  UART_S.println("start_test");
  timer = millis();
  int c = 0;
 //enlight red
  ledsBlue();
  // after all is pushed or after timer - finish
  while (c < maxCapacitiveSensors && millis() - timer < TEST_MINUTES * 60000) {
    readSerial();

    uint8_t touched = cap.touched();

     // Touch detected
    if (touched != 0) {
      for (uint8_t i = 0; i < maxCapacitiveSensors; i++) {
          // if button pushed as unar operation 
        if (touched & (1 << i)) {
          if (buttonPushed[i] == false) {
            buttonPushed[i] = true;
            c++;
            setButtonColor(i, leds.Color(200, 0, 0));
            delay(1000);
            break;
          }
        }
      }
      cap.touched(); //reset dubble press
      delay(10);
    }

  }
  delay(500);
  cap.touched(); //reset dubble press
  ledsOff();
  timer = 0;
   // define all Sensors unpushed
  for (int i = 0;i < maxCapacitiveSensors;i++) {
    buttonPushed[i] = false;
  }
  UART_S.println("finish_test");
}

void finishGame() {
  lvl = 4;
  timer = 0;
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
      else if (inData.startsWith("run")) {
        startGame();
      }
      else if (inData.startsWith("reset")) {
        digitalWrite(LOGO_OPEN, HIGH);
        lvl = 1;
        timer = 0;
        ledsOff();
      }
      else if (inData.startsWith("test")) {
        startTest();
      }
      else if (inData.startsWith("finish")) {
        finishGame();
      }

      inData = ""; // Clear recieved buffer
    }
    else {
      inData += recieved;
    }
  }
}

// -------------------     S E T U P    -------------------------


void ledInit() {
  leds.begin();
  leds.clear();
  for (int i = 0; i < PIXEL_NUM; i++) { // For each pixel...
    leds.setPixelColor(i, leds.Color(0, 150, 0));
    leds.show();   // Send the updated pixel colors to the hardware.
    delay(200); // Pause before next pass through loop
  }
  leds.clear();
  leds.show();
}

void setup() {
  pinMode(LOGO_OPEN, OUTPUT);
  digitalWrite(LOGO_OPEN, HIGH);

  UART_S.begin(9600);
  UART_S.println("load");

  ledInit();

  setCode();

  capacitiveSensorsInit();

  lvl = 1;
  timer = 0;
  delay(startupDelay);

  UART_S.println("init");
  /*
  for (int j=0; j<codeLength; j++)
    UART_S.print(String(code[j]));
    UART_S.println();
  */
}

// compare x sign arrays
bool arrayCompare(int a[], int b[], int x = codeLength) {
  bool match = false;
  if (a[0] != NULL && b[0] != NULL) // Make sure there is something in the array first
    match = true; // Assume they match at first
  for (int k = 0; k < x; k++) { // Loop 4 times
    if (a[k] != b[k]) { // IF a != b then set match = false, one fails, all fail
      match = false;
      break;
    }
  }
  if (match) // Check to see if if match is still true
    return true; // Return true
  return false; // Return false
}

void checkGameResult(void) {
  if (counter < codeLength)
    return;

// reset counter    
  counter = 0;

  // check code
  if (arrayCompare(input, code)) {
    lvl = 3;
    UART_S.println("finish");
  }
  else {
    startGame();
  }

  // reset pushed state
  for (int i = 0;i < maxCapacitiveSensors;i++)
    buttonPushed[i] = false;

  delay(buttonCoolDownDelay);

  // disable dubbling in readings
  // read last I2C data to reset; 
  cap.touched();
}

// set pixel color
void setButtonColor(byte StickNum, uint32_t color) {

  byte StartPixel = StickNum * PIXEL_IN_STICK;

  for (byte i = StartPixel; i < (StartPixel + PIXEL_IN_STICK); i++)
    leds.setPixelColor(i, color);
  leds.show();
}

void checkSensors(void) {

  uint8_t touched = cap.touched();

  // No touch detected
  if (touched == 0)
    return;

  for (uint8_t i = 0; i < maxCapacitiveSensors; i++) {
      // if button pushed as unar operation 
    if (touched & (1 << i)) {
        // if button was not pushed earlier
      if (buttonPushed[i] == false) {
        buttonPushed[i] = true; // set flag
        input[counter++] = i + 1;

        // UART_S.print("c_"); Serial.print(i + 1); Serial.print("\t");
        // for (int j; j < 4; j++) {
        //   UART_S.print(input[j]);
        //   UART_S.print(" ");
        // }
        // UART_S.println();

      // Moderately bright blue color.
        setButtonColor(i, leds.Color(0, 0, 200));
        delay(buttonCoolDownDelay);

        UART_S.print("input:");
        for (byte j = 0;j < counter;j++) {
          UART_S.print(nums[input[j] - 1]);
        }
        UART_S.println();

        break;
      }
    }
  }
  checkGameResult();
}

void doneGame() {
    // start timer
  if (timer == 0) timer = millis();
  // Dimm LED
  ledsOff();
  // Open logo
  digitalWrite(LOGO_OPEN, LOW);

  // finished signal
  if (millis() - timer < DONE_DELAY) {

  }
  else {
    finishGame();
  }
}

// -------------------     L O O P    -------------------------

void loop() {
  readSerial();
  switch (lvl) {
  case 1:
    break;
  case 2:
    // playGame
    checkSensors();
    break;
  case 3:
    doneGame();
    break;
  case 4:
  default:
    break;
  }
  delay(50); // delay before next scan
}
