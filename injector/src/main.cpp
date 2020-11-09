#include "FastLED.h"
#include <IRremote.h>

#define SPEAD_COLOR_CHANGE 48  // скорость
#define COLOR_RND_TIMER 5 // Как часто менять палитру в секундах
#define IR_RECEIVE_PIN A2 // Пин для IR приемника
#define LED_PIN     12 // Пин для светодиодов WS2812
#define BRIGHTNESS  255 // Яркость
#define LED_TYPE    WS2812
#define COLOR_ORDER GRB
#define NUM_LEDS 10
#define BASE_COLOR 200
 
struct CRGB leds[NUM_LEDS];
 
CRGBPalette16 currentPalette(CRGB::Black);
CRGBPalette16 targetPalette(OceanColors_p);
 
IRrecv irrecv(IR_RECEIVE_PIN);
decode_results results;

byte prewMode = 0;
byte mode = 0;
byte VALUE = 0;

byte color_setting[5][4] = {
  {0,0,0,0},
  {255,230,180,200},
  {255,255,255,255},
};

 
void uppdatePalette(){
  if(prewMode == 0 and mode == 0) return;
  Serial.println("uppdatePalette");
  prewMode = mode;

  targetPalette = CRGBPalette16(CHSV(BASE_COLOR + random16(10), 255, 255),   // Create palettes with similar colours.
                                CHSV(85*2 + random16(10), 255, 255),
                                CHSV(BASE_COLOR + random16(10), 255, 255),
                                CHSV(0, 255, 255));                                
}

void setup() {
  Serial.begin(115200);
  while (!Serial)
  delay(500);

  // Just to know which program is running on my Arduino
  Serial.println(F("START " __FILE__ " from " __DATE__ __TIME__));

  // In case the interrupt driver crashes on setup, give a clue
  // to the user what's going on.
  Serial.println("Enabling IRin");
  irrecv.enableIRIn(); // Start the receiver

  LEDS.addLeds<LED_TYPE,LED_PIN,COLOR_ORDER>(leds,NUM_LEDS);
 
  LEDS.setBrightness(BRIGHTNESS);

  uppdatePalette();
}
 
void fillnoise8() { 
  if(mode == 10){
    byte scale = COLOR_RND_TIMER*6;
    for(int i = 0; i < NUM_LEDS; i++) {                                       // Just ONE loop to fill up the LED array as all of the pixels change.
      uint8_t index = inoise8(i*scale, millis()/10+i*scale);                   // Get a value from the noise function. I'm using both x and y axis.
      leds[i] = ColorFromPalette(currentPalette, index, 255, LINEARBLEND);    // With that value, look up the 8 bit colour palette value and assign it to the current LED.
    }
  }else{
    for(int i = 0; i < mode; i++) {
      leds[i] = CHSV(BASE_COLOR, 255, 255);
    }
    for(int i = mode; i < NUM_LEDS; i++) { 
      leds[i] = 0;
    }    
  }
 
} // fillnoise8()

void setMode(byte m){
  mode = m;
  Serial.println(mode, HEX);
  
  if(mode<NUM_LEDS){
    for(int i = 0; i < NUM_LEDS; i++) {
      if(i<mode){
        currentPalette[i] = leds[i];
      }
    }
  }else{
    uppdatePalette();
  }
}

void loop() {
  //if(prewMode > 0 or mode > 0){ //перерисовка если нужно что то рисовать
  {
    fillnoise8();  

    EVERY_N_MILLIS(100) {
      nblendPaletteTowardPalette(currentPalette, targetPalette, SPEAD_COLOR_CHANGE);          // Blend towards the target palette over 48 iterations.
      LEDS.show();
    }
  
    EVERY_N_SECONDS(COLOR_RND_TIMER/5) {                                                      
      // Change the target palette to a random one every N seconds.
      uppdatePalette();
    }
  }

  if (irrecv.decode(&results)) {
    if(results.value != 0xFFFFFFFF){
      unsigned long value = results.value-0xa90;

      Serial.println(value, HEX);
      if(value>=0 and value<=NUM_LEDS){
        setMode(value);
      }
      // if(results.value == 0xC12FE11E) setMode(0);
      // if(results.value == 0xC12F26D9) setMode(1);
    }
    irrecv.resume();
  }
}
 