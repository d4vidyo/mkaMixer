#include <FastLED.h>
#define ChannelNumbers 4
#define LED_PIN 2
CRGB leds[ChannelNumbers];
#define brightness 100
#define red 0
#define green 96
#define blue 160

enum status { unknown,
              notSet,
              noAudioSession,
              active };

class Button {
public:
  int pin;
  unsigned long start = 0;
  unsigned long holdTimer = 0;
  unsigned long doubleStart = 0;
  unsigned long doubleTimer = 0;

  Button(int pin) {
    this->start = 0;
    this->holdTimer = 0;
    this->pin = pin;
  }
};

class Channel {
public:
  float Volume = 100;
  bool Mute = false;
  status state = notSet;
  status previous = notSet;
  int blinkCount = 0;
  int potiPin;
  Button* button;

  Channel() {
    this->button = new Button(3);
    this->potiPin = 0;
  }
  Channel(int buttonPin, int poti) {
    this->button = new Button(buttonPin);
    this->potiPin = poti;
  }

  ~Channel() {
    delete button;
  }
};
Channel* channels[ChannelNumbers];

void setup() {
  Serial.begin(9600);
  pinMode(3, INPUT_PULLUP);
  pinMode(4, INPUT_PULLUP);
  pinMode(5, INPUT_PULLUP);
  pinMode(6, INPUT_PULLUP);

  for (int i = 0; i < ChannelNumbers; i++) {
    channels[i] = new Channel(3 + i, i);
  }

  FastLED.addLeds<WS2812B, LED_PIN, GRB>(leds, ChannelNumbers);
  FastLED.setBrightness(brightness);
  FastLED.show();

  Serial.println("ready");
}

void loop() {
  for (int i = 0; i < ChannelNumbers; i++) {
    checkButton(i);
    checkPoti(i);
  }
  checkForMessages();
  updateLEDs();
}

void checkButton(int channel) {
#define holdTime 500
#define pressTime 25
#define doubleTime 500
#define unsignedLongMax 4294967295

  if (channels[channel]->button->doubleTimer != unsignedLongMax) {
    channels[channel]->button->doubleTimer = millis() - channels[channel]->button->doubleStart;
    if (channels[channel]->button->doubleTimer > doubleTime) {
      channels[channel]->button->doubleTimer = unsignedLongMax;
    }
  }

  bool pressed = !digitalRead(channels[channel]->button->pin);

  if (!pressed) {
    channels[channel]->button->start = millis();
    if (channels[channel]->button->holdTimer >= pressTime && channels[channel]->button->holdTimer < holdTime) {
      Single(channel);

      if (channels[channel]->button->doubleTimer == unsignedLongMax) {
        channels[channel]->button->doubleStart = millis();
        channels[channel]->button->doubleTimer = 0;
      } else {
        DoublePress(channel);
      }
    }
    channels[channel]->button->holdTimer = 0;
  } else if (channels[channel]->button->holdTimer != unsignedLongMax) {
    channels[channel]->button->holdTimer = millis() - channels[channel]->button->start;
    if (channels[channel]->button->holdTimer >= holdTime) {
      Hold(channel);
      channels[channel]->button->holdTimer = unsignedLongMax;
    }
  }

  /*
#define holdTime 500
#define pressTime 25
#define doubleTime 500
#define unsignedLongMax 4294967295
  static unsigned long start = 0;
  static unsigned long holdTimer = 0;
  static unsigned long doubleStart = 0;
  static unsigned long doubleTimer = unsignedLongMax;

  bool pressed = !digitalRead(3);

  if (doubleTimer != unsignedLongMax) {
    doubleTimer = millis() - doubleStart;
    if (doubleTimer > doubleTime) {
      doubleTimer = unsignedLongMax;
    }
  }

  if (!pressed) {
    start = millis();
    if (holdTimer >= pressTime && holdTimer < holdTime) {
      leds[3] = CHSV(green, 255, brightness);
      Serial.println("Once");

      if (doubleTimer == unsignedLongMax) {
        doubleStart = millis();
        doubleTimer = 0;
      } else {
        leds[3] = CHSV(red, 255, brightness);
        Serial.println(doubleTimer);
      }
    }
    holdTimer = 0;
  } else if (holdTimer != unsignedLongMax) {
    holdTimer = millis() - start;
    if (holdTimer >= holdTime) {
      leds[3] = CHSV(blue, 255, brightness);
      Serial.println("hold");
      holdTimer = unsignedLongMax;
    }
  }
  */
}

void Hold(int channel) {
  channels[channel]->previous = channels[channel]->state;
  channels[channel]->state = unknown;
  Serial.println((String)channel + " SET");
}

void Single(int channel) {
  channels[channel]->Mute = !channels[channel]->Mute;
  if (channels[channel]->Mute) {
    Serial.println((String)channel + " 0");
  } else {
    Serial.println((String)channel + " " + (String)channels[channel]->Volume);
  }
}

void DoublePress(int channel) {
  Serial.println((String)channel + " DOUBLE");
}

void checkPoti(int channel) {
#define sensitivity 10
  static int reading[ChannelNumbers] = { 0 };
  int newReading = analogRead(channels[channel]->potiPin);
  if (newReading >= reading[channel] + sensitivity || newReading <= reading[channel] - sensitivity) {
    reading[channel] = newReading;
  } else {
    return;
  }

  float volume = reading[channel] / 10.23;
  channels[channel]->Volume = volume;
  if (!channels[channel]->Mute) {
    Serial.println((String)channel + " " + (String)volume);
  }
}

void checkForMessages() {
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil("\n");
    int seperator = input.indexOf(" ");
    int channel = input.substring(0, seperator).toInt();
    String message = input.substring(seperator + 1, input.length());
    message.replace("\n", "");
    if (message == "SET_Succes") {
      Serial.println((String)channel + " " + (String)channels[channel]->Volume);
      channels[channel]->state = active;
    } else if (message == "SET_Failed") {
      channels[channel]->state = channels[channel]->previous;
      channels[channel]->blinkCount = 4;
    } else if (message == "NoAudioSession") {
      channels[channel]->state = noAudioSession;
    } else if (message == "notActive") {
      channels[channel]->state = notSet;
    } else if (message == "active") {
      Serial.println((String)channel + " " + (String)channels[channel]->Volume);
      channels[channel]->state = active;
    }
  }
}

void updateLEDs() {
  static int timer = millis();
  int newTime = millis();
  if (newTime - timer < 16) {
    return;
  }

  for (int i = 0; i < ChannelNumbers; i++) {
    int ledNr = ChannelNumbers - 1 - i;
    switch (channels[i]->state) {
      case unknown:
        blinkBlue(i);
        break;
      case notSet:
        leds[ledNr] = CHSV(0, 255, 0);
        break;
      case noAudioSession:
        leds[ledNr] = CHSV(blue, 255, brightness);
        break;
      case active:
        leds[ledNr] = CHSV(green, 255, brightness);
        break;
    }
    if (channels[i]->Mute) {
      leds[ledNr] = CHSV(red, 255, brightness);
    }
    if (channels[i]->blinkCount != 0) {
      blinkRed(i);
    }
  }

  FastLED.show();
  timer = millis();
}

void blinkBlue(int channel) {
  int ledNr = ChannelNumbers - 1 - channel;
  static int timer[ChannelNumbers] = { 0 };
  int newTime = millis();
  if (newTime - timer[channel] < 300) {
    leds[ledNr] = CHSV(blue, 255, brightness);
    return;
  }
  timer[channel] = millis();
  leds[ledNr] = CHSV(blue, 255, 0);
}

void blinkRed(int channel) {
#define period 500
  int ledNr = ChannelNumbers - 1 - channel;
  static long timer[ChannelNumbers] = { 0 };
  long newTime = millis();
  long delta = newTime - timer[channel];
  if (delta > 2 * period) {
    leds[ledNr] = CHSV(red, 255, 0);
    timer[channel] = millis();
    channels[channel]->blinkCount--;
  } else if (delta > period) {
    leds[ledNr] = CHSV(red, 255, brightness);
  } else if (delta > 0) {
    leds[ledNr] = CHSV(red, 255, 0);
  }
}
