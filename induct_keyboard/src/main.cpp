#include <Arduino.h>

long pcounterA;
byte pins_cnt=1;
uint8_t pins_in[]={13, 3};
byte pr_st[]={0,0};

void setup() {
  Serial.begin(9600);
  for (byte i =0; i<pins_cnt;i++){ 
    pinMode(pins_in[i],INPUT); 
  }
  delay(1000);
  for (byte i =0; i<pins_cnt;i++){
    pr_st[i] = digitalRead(pins_in[i]); 
  }
}

void loop() {
  for (byte i =0; i<pins_cnt;i++){
    byte st = digitalRead(pins_in[i]); 
    if(pr_st[i]!=st){
      pr_st[i]==st;
      if(not st){
        Serial.println(i);
      }
    }
  }
}