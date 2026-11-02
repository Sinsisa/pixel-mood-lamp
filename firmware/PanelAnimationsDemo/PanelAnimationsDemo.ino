#include <Adafruit_NeoPixel.h>

// Project A: low-power 15 x 15 animation demo for the CURRENT setup.
// Arduino Uno D6 -> panel DATA.
// Panel power remains on the separate MB102 5 V output with common GND.
// This deliberately keeps the global brightness at 8/255.

constexpr uint8_t DATA_PIN = 6;
constexpr uint8_t WIDTH = 15;
constexpr uint8_t HEIGHT = 15;
constexpr uint16_t LED_COUNT = WIDTH * HEIGHT;
constexpr uint8_t DEMO_BRIGHTNESS = 8;

Adafruit_NeoPixel panel(LED_COUNT, DATA_PIN, NEO_GRB + NEO_KHZ800);

// The electrical chain snakes left/right on alternate rows.
uint16_t XY(uint8_t x, uint8_t y) {
  if (y & 1) {
    x = WIDTH - 1 - x;
  }
  return static_cast<uint16_t>(y) * WIDTH + x;
}

void setXY(uint8_t x, uint8_t y, uint32_t colour) {
  if (x < WIDTH && y < HEIGHT) {
    panel.setPixelColor(XY(x, y), colour);
  }
}

void showSmiley(bool wink) {
  panel.clear();
  const uint32_t yellow = panel.Color(255, 150, 0);

  // Filled circular face. Radius 6 on the 15 x 15 grid.
  for (int8_t y = 0; y < HEIGHT; ++y) {
    for (int8_t x = 0; x < WIDTH; ++x) {
      const int8_t dx = x - 7;
      const int8_t dy = y - 7;
      if (dx * dx + dy * dy <= 36) {
        setXY(x, y, yellow);
      }
    }
  }

  // Dark eyes cut out of the illuminated face.
  setXY(4, 5, 0);
  setXY(4, 6, 0);
  if (wink) {
    setXY(9, 6, 0);
    setXY(10, 6, 0);
    setXY(11, 6, 0);
  } else {
    setXY(10, 5, 0);
    setXY(10, 6, 0);
  }

  // Curved smile.
  setXY(4, 9, 0);
  setXY(5, 10, 0);
  setXY(6, 11, 0);
  setXY(7, 11, 0);
  setXY(8, 11, 0);
  setXY(9, 10, 0);
  setXY(10, 9, 0);

  panel.show();
}

uint32_t colourWheel(uint8_t position) {
  position = 255 - position;
  if (position < 85) {
    return panel.Color(255 - position * 3, 0, position * 3);
  }
  if (position < 170) {
    position -= 85;
    return panel.Color(0, position * 3, 255 - position * 3);
  }
  position -= 170;
  return panel.Color(position * 3, 255 - position * 3, 0);
}

void rainbow(uint8_t frameCount) {
  for (uint8_t frame = 0; frame < frameCount; ++frame) {
    for (uint16_t pixel = 0; pixel < LED_COUNT; ++pixel) {
      panel.setPixelColor(
          pixel,
          colourWheel(static_cast<uint8_t>((pixel * 256UL / LED_COUNT) + frame * 4)));
    }
    panel.show();
    delay(35);
  }
}

void showDimFullPanel(uint32_t colour, uint16_t holdMs) {
  panel.fill(colour);
  panel.show();
  delay(holdMs);
  panel.clear();
  panel.show();
  delay(150);
}

void setup() {
  pinMode(DATA_PIN, OUTPUT);
  digitalWrite(DATA_PIN, LOW);

  panel.begin();
  panel.setBrightness(DEMO_BRIGHTNESS);
  panel.clear();
  panel.show();
}

void loop() {
  showSmiley(false);
  delay(1800);
  showSmiley(true);
  delay(500);
  showSmiley(false);
  delay(1000);

  // All 225 LEDs are on, but still globally limited to 8/255.
  showDimFullPanel(panel.Color(255, 0, 0), 700);
  showDimFullPanel(panel.Color(0, 255, 0), 700);
  showDimFullPanel(panel.Color(0, 0, 255), 700);

  rainbow(80);

  panel.clear();
  panel.show();
  delay(500);
}
