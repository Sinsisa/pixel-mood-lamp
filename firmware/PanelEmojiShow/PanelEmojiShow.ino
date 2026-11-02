#include <Adafruit_NeoPixel.h>
#include "EmojiShowData.h"

// Project A / 225-pixel emoji show / 18-second repeating timeline.
// Uno D6 -> panel DATA; panel and Uno share GND. Same map as the proven demo.
// Animation preview: visualizations/panel-emoji-show.html.
// Frame art and timing are generated from tools/build_emoji_animation.py.
constexpr uint8_t DATA_PIN = 6;
constexpr uint8_t DEMO_BRIGHTNESS = 30;  // 0..255; existing low-load test default.
constexpr uint8_t WIDTH = 15;
constexpr uint8_t HEIGHT = 15;
constexpr uint16_t LED_COUNT = WIDTH * HEIGHT;

Adafruit_NeoPixel panel(LED_COUNT, DATA_PIN, NEO_GRB + NEO_KHZ800);
uint16_t timelineIndex = 0;
uint32_t nextFrameAt = 0;

#if defined(__AVR_ATmega328P__) && F_CPU == 16000000UL
// NeoPixel transmission masks interrupts, so Uno millis() loses time while
// sending 225 pixels. Timer1 keeps counting through show(). This standalone
// sketch reserves Timer1: do not add Servo or Timer1 PWM without changing this.
constexpr uint16_t CLOCK_TICKS_PER_MS = 250;  // Timer1 /64 = one tick per 4 us.
uint16_t lastCounter = 0;
uint32_t elapsedTicks = 0;

void beginAnimationClock() {
  TCCR1A = 0;
  TCCR1B = 0;
  TIMSK1 = 0;
  TCNT1 = 0;
  TIFR1 = _BV(TOV1);
  TCCR1B = _BV(CS11) | _BV(CS10);
  lastCounter = TCNT1;
}

uint32_t animationClock() {
  const uint16_t counter = TCNT1;
  elapsedTicks += uint16_t(counter - lastCounter);
  lastCounter = counter;
  // Called continuously; no blocking operation lasts Timer1's 262 ms wrap.
  return elapsedTicks;
}
#else
constexpr uint16_t CLOCK_TICKS_PER_MS = 1;
void beginAnimationClock() {}
uint32_t animationClock() { return millis(); }
#endif

uint16_t pixelIndex(uint8_t x, uint8_t y) {
  return uint16_t(y) * WIDTH + ((y & 1) ? WIDTH - 1 - x : x);
}

void drawFrame(uint8_t frame) {
  for (uint16_t pixel = 0; pixel < LED_COUNT; ++pixel) {
    const uint8_t packed = pgm_read_byte(&EMOJI_FRAMES[frame][pixel / 2]);
    const uint8_t colour = (pixel & 1) ? packed & 0x0f : packed >> 4;
    const uint8_t red = pgm_read_byte(&EMOJI_PALETTE[colour][0]);
    const uint8_t green = pgm_read_byte(&EMOJI_PALETTE[colour][1]);
    const uint8_t blue = pgm_read_byte(&EMOJI_PALETTE[colour][2]);
    panel.setPixelColor(pixelIndex(pixel % WIDTH, pixel / WIDTH), red, green, blue);
  }
  panel.show();
}

void setup() {
  pinMode(DATA_PIN, OUTPUT);
  digitalWrite(DATA_PIN, LOW);
  panel.begin();
  panel.setBrightness(DEMO_BRIGHTNESS);
  panel.clear();
  panel.show();
  beginAnimationClock();
  nextFrameAt = animationClock();
}

void loop() {
  const uint32_t now = animationClock();
  if (int32_t(now - nextFrameAt) < 0) return;

  // Deadlines advance from the previous deadline, not the end of show().
  // Skip stale holds if another task takes time, retaining the animation phase.
  uint8_t frame = 0;
  do {
    frame = pgm_read_byte(&EMOJI_TIMELINE[timelineIndex].frame);
    nextFrameAt += uint32_t(pgm_read_word(&EMOJI_TIMELINE[timelineIndex].duration))
                   * CLOCK_TICKS_PER_MS;
    timelineIndex = (timelineIndex + 1) % TIMELINE_COUNT;
  } while (int32_t(now - nextFrameAt) >= 0);
  drawFrame(frame);
}
