//int ledPins[8] = {3,5,6,9,10,11,12,13};

#include "FastLED.h"

// How many leds are in the strip?
#define NUM_LEDS 300
#define LED_TYPE    WS2812B

// Data pin that led data will be written out over
#define DATA_PIN 3

// This is an array of leds.  One item for each led in your strip.
CRGB leds[NUM_LEDS];

String readString;

void setup() {
  Serial.begin(57600);
  delay(1000);
  FastLED.addLeds<LED_TYPE, DATA_PIN, GRB>(leds, NUM_LEDS);

  //beauty start
  for (int i = 1; i <= NUM_LEDS / 2; i++) {
    leds[i-1] = CHSV( 145, 200, 200);
    FastLED.show();
    //delay(10);
  }
  for (int i = 1; i <= NUM_LEDS / 2; i++) {
    leds[i-1] = CHSV( 0, 0, 0);
    FastLED.show();
    //delay(10);
  }
  delay(1000);
}


void loop() {
  // serial read section
  while (Serial.available()) // this will be skipped if no data present, leading to
                             // the code sitting in the delay function below
  {
    delay(5);  //delay to allow buffer to fill 
    if (Serial.available() >0)
    {
      char c = Serial.read();  //gets one byte from serial buffer
      readString += c; //makes the string readString
    }
  }
  if (readString.length() >0)
  {
    
    //Serial.print("Arduino received: ");  
    
    //Serial.print(readString);  
    //int intchar = readString.toInt();

    int song = readString[0]; //какой номер песни включён 
    int mode = readString[1]; //какой режим мигания включён    
    int ledInItem = NUM_LEDS / 8; //кол-во лампочек одного диапазона звука
    CHSV light = CHSV( 0, 0, 0);
    for (int i = 2; i <= 9; i++) {
      int li = readString[i] - '0';
      int lightness = 0;
      if(li > 2)
        lightness = 20;
      if(li == 5)
        lightness = 50;
      if(li == 6)
        lightness = 150;
      if(li == 7)
        lightness = 200;
      if(li == 8)
        lightness = 255;
      int item = i-2; //light item count from zero
      int color = map(li, 3, 8, 145, 20);
      if(li == 0) {
        light = CHSV( 0, 0, 0);
      } else {
        light = CHSV( color, 255, lightness);
      }
      //цилк по всем ветодиодам в группе одного диапазона звука
      for (int itemNumber = 0; itemNumber <= ledInItem - 1; itemNumber++) {
        leds[item*ledInItem + itemNumber] = light;
      }
    }
    FastLED.show();
    //Serial.flush();
    readString = "";
  } else {
    //digitalWrite(2, LOW);
  }
  
}
