import time
from rpi_ws281x import *
import argparse
import numpy as np

# LED strip configuration:
LED_COUNT      = 30     # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating a signal (try 10)
LED_BRIGHTNESS = 65      # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

def createDigit():
    w, h = 39, 75
    digit = np.zeros((h, w), dtype=int)
    index = 1

    # Upper left, bottom to top
    for i in range(h):
        digit[74 - i][0] = index
        index += 1
        
    # Across to right
    for i in range(w - 1):
        digit[0][i + 1] = index
        index += 1
        
    # Down to half
    for i in range(h//2):
        digit[i + 1][w - 1] = index
        index += 1
        
    # Across to left
    for i in range(w - 2):
        digit[h//2][w - i - 2] = index
        index += 1
        
    # Across to right
    for i in range(w - 2):
        digit[h//2 + 1][i + 1] = index
        index += 1
        
    # Down to bottom
    for i in range(h//2):
        digit[h//2 + i + 1][w - 1] = index
        index += 1
    
    # Across to left
    for i in range(w - 2):
        digit[h - 1][w - i - 2] = index
        index += 1

    # Print the digit
    for i in range(h):
        for j in range(w):
            print(digit[i][j], end=" ")
        print()
    
    return digit

def writeDigit(digit, number=0):
    h, w = digit.shape
    
    top = digit[0][:]
    left_top = digit[0: h//2, 0]
    left_bottom = digit[h//2: h, 0]
    middle = digit[h//2: h//2 + 2, 1: w - 1].flatten()
    right_top = digit[0: h//2, w - 1]
    right_bottom = digit[h//2: h, w - 1]
    bottom = digit[h - 1][:]
    
    top_indexes = di
    
    if number == 1:
        mask = np.zeros((h, w), dtype=int)
        # Use right_top and right_bottom to create mask
    
    print(middle)

def changeColumn(strip, digit):
    h, w = digit.shape
    
    for i in range(w):
        column = digit[:, i]
        
        for index in column:
            if index != 0:
                strip.setPixelColor(index - 1, Color(255, 0, 0))
                
        strip.show()

        time.sleep(0.3)

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, color)
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i+j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256*iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, wheel((i+j) % 255))
            strip.show()
            time.sleep(wait_ms/1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i+q, 0)

# Main program logic follows:
if __name__ == '__main__':
    digit = createDigit()
    
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # # Intialize the library (must be called once before other functions).
    strip.begin()

    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    changeColumn(strip, digit)
    
    # writeDigit(digit)
    
    # try:

    #     while True:
    #         print ('Color wipe animations.')
    #         colorWipe(strip, Color(255, 0, 0))  # Red wipe
    #         colorWipe(strip, Color(0, 255, 0))  # Blue wipe
    #         colorWipe(strip, Color(0, 0, 255))  # Green wipe
    #         print ('Theater chase animations.')
    #         theaterChase(strip, Color(127, 127, 127))  # White theater chase
    #         theaterChase(strip, Color(127,   0,   0))  # Red theater chase
    #         theaterChase(strip, Color(  0,   0, 127))  # Blue theater chase
    #         print ('Rainbow animations.')
    #         rainbow(strip)
    #         rainbowCycle(strip)
    #         theaterChaseRainbow(strip)

    # except KeyboardInterrupt:
    #     if args.clear:
    #         colorWipe(strip, Color(0,0,0), 10)
