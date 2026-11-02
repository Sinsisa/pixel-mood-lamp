#include <Adafruit_NeoPixel.h>

// Project A manufactured LED-panel first-power test.
// Arduino Uno: D6 -> external series resistor -> panel DATA.
// The panel must use its own regulated 5 V supply and share GND with the Uno.

constexpr uint8_t DATA_PIN = 6;
constexpr uint16_t LED_COUNT = 225;
constexpr uint8_t CHANNEL_LEVEL = 8;  // 8/255: deliberately very dim
constexpr uint16_t STEP_MS = 20;      // 4.5 seconds per complete colour pass
constexpr uint16_t PAUSE_MS = 400;

Adafruit_NeoPixel panel(LED_COUNT, DATA_PIN, NEO_GRB + NEO_KHZ800);

void allOff() {
  panel.clear();
  panel.show();
}

void testColour(uint8_t red, uint8_t green, uint8_t blue,
                const __FlashStringHelper* colourName) {
  Serial.print(F("Starting "));
  Serial.print(colourName);
  Serial.println(F(" pass"));

  for (uint16_t index = 0; index < LED_COUNT; ++index) {
    // clear() guarantees that no more than one LED is commanded on.
    panel.clear();
    panel.setPixelColor(index, panel.Color(red, green, blue));
    panel.show();

    Serial.print(F("Testing L"));
    Serial.println(index + 1);
    delay(STEP_MS);
  }

  allOff();
  delay(PAUSE_MS);
}

void setup() {
  // Establish a defined low data output before starting the LED library.
  pinMode(DATA_PIN, OUTPUT);
  digitalWrite(DATA_PIN, LOW);

  Serial.begin(115200);
  panel.begin();
  allOff();
  delay(500);

  Serial.println(F("Project A: 225-pixel first-power test"));
  Serial.println(F("Only one dim LED is commanded on at a time."));
}

void loop() {
  testColour(CHANNEL_LEVEL, 0, 0, F("RED"));
  testColour(0, CHANNEL_LEVEL, 0, F("GREEN"));
  testColour(0, 0, CHANNEL_LEVEL, F("BLUE"));
}
