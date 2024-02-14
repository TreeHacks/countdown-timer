import time
from rpi_ws281x import *
import argparse
import numpy as np
import math
from datetime import datetime
import threading
import rainbow
import sys

# LED strip configuration:
LED_COUNT      = 1800     # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating a signal (try 10)
LED_BRIGHTNESS = 65      # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

def printArray(array):
    shape = array.shape
    
    for i in range(shape[0]):
        for j in range(shape[1]):
            print(array[i][j], end=" ")
        print()
        
def runDigit(strip, wait_ms=50):
    global digit
    
    while True:
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        # print("Current Time =", current_time)

        writeDigit(int(current_time[-1]))
        
        #printArray(digit)
        
        #for i in range(digit.shape[0]):
        #    for j in range(digit.shape[1]):
        #        strip.setPixelColor(int(digit[i][j]), Color(255, 0, 0))
        
        #strip.show()

        time.sleep(0.05)

def createDigit():
    w, h = 37, 75
    digit = np.zeros((h, w), dtype=int)
    index = 1
        
    # Across to right
    for i in range(w - 2):
        digit[h//2][i + 1] = index
        index += 1
        
    # Up to top right
    for i in range(h//2 + 1):
        digit[h//2 - i][w - 1] = index
        index += 1
        
    # Across to left
    for i in range(w - 2):
        digit[0][w - i - 2] = index
        index += 1
        
    # Down to bottom left
    for i in range(h):
        digit[i][0] = index
        index += 1
        
    # Across to right
    for i in range(w - 2):
        digit[h - 1][i + 1] = index
        index += 1
        
    # Up to middle right
    for i in range(math.ceil(h/2 - 1)):
        digit[h - 1 - i][w - 1] = index
        index += 1
    
    return digit

def writeDigit(number=0):
    """
    Set the digit to a number from 0 to 9 using the digit mask
    """
    global lock
    global digit
    global color_cache
    
    h, w = digit.shape
    
    middle = np.s_[h//2, 1:w-1]
    right_top = np.s_[:h//2 + 1, w-1]
    top = np.s_[0, 1:w - 1]
    left_top = np.s_[:h//2 + 1, 0]
    left_bottom = np.s_[h//2 + 1:, 0]
    bottom = np.s_[h - 1, 1:w - 1]
    right_bottom = np.s_[h//2 + 1:, w-1]
    
    mask = np.zeros((h, w), dtype=int)
    
    lock.acquire()
    
    if number == 0:
        mask[right_bottom] = 1
        mask[left_top] = 1
        mask[top] = 1
        mask[right_top] = 1
        mask[left_bottom] = 1
        mask[bottom] = 1
    elif number == 1:
        mask[right_top]= 1
        mask[right_bottom] = 1
    elif number == 2:
        mask[middle] = 1
        mask[right_top] = 1
        mask[left_bottom] = 1
        mask[top] = 1
        mask[bottom] = 1
    elif number == 3:
        mask[middle] = 1
        mask[right_top] = 1
        mask[top] = 1
        mask[bottom] = 1
        mask[right_bottom] = 1
    elif number == 4:
        mask[left_top] = 1
        mask[middle] = 1
        mask[right_top] = 1
        mask[right_bottom] = 1
    elif number == 5:
        mask[middle] = 1
        mask[left_top] = 1
        mask[top] = 1
        mask[bottom] = 1
        mask[right_bottom] = 1
    elif number == 6:
        mask[middle] = 1
        mask[left_top] = 1
        mask[top] = 1
        mask[bottom] = 1
        mask[left_bottom] = 1
        mask[right_bottom] = 1
    elif number == 7:
        mask[top] = 1
        mask[right_top] = 1
        mask[right_bottom] = 1
    elif number == 8:
        mask[middle] = 1
        mask[left_top] = 1
        mask[top] = 1
        mask[bottom] = 1
        mask[left_bottom] = 1
        mask[right_bottom] = 1
        mask[right_top] = 1
    elif number == 9:
        mask[middle] = 1
        mask[left_top] = 1
        mask[top] = 1
        mask[bottom] = 1
        mask[right_bottom] = 1
        mask[right_top] = 1
    
    # Create a mask of the digit    
    digit = np.where(mask, digit_indices, 0)
    
    # Turn on the LEDs that are part of the digit
    for i in range(h):
        for j in range(w):
            if digit[i][j] != 0:
                cached = color_cache[i][j]
                if cached != 0:
                    strip.setPixelColor(int(digit[i][j] - 1), cached)
    
    # Create the anti-mask of the digit
    anti_mask = np.where(mask, 0, digit_indices)

    # Turn off the LEDs that are not part of the digit
    for i in range(h):
        for j in range(w):
            if digit[i][j] == 0:
                strip.setPixelColor(int(anti_mask[i][j] - 1), Color(0, 0, 0))

    strip.show()

    lock.release()
    
def patterns(strip, wait_ms=50):
    global digit
    
    h, w = digit.shape
    
    #colors = 
    
    index = 0
    
    print()
    
    while True:
        #printArray(digit)
        #print()
        
        # Rainbow
        for j in range(256):
            arr = (digit != 0).astype(int)
            
            if j > 0:
                # Move cursor h rows up in terminal
                sys.stdout.write("\033[F" * (h-1))
                    
            height_arr = list(range(h))
            #height_arr.reverse() if j % 2 == 0 else height_arr
                    
            for i in height_arr:
                color = wheel_tuple((i+j) & 255)
                color = rgb_to_hex(color)
                
                strip_color = wheel((i + 3 * j) & 255)
                
                #print(f"Col {i} color: {color}")
                # rainbow.print(f"Col {index} color: {color}", color=color)
                
                for k in range(w):
                    #strip.setPixelColor(int(digit[i][k] - 1), strip_color)
                
                    change_color(strip_color, i, k)
                    
                """
                for k in range(w):
                    if arr[i][k]:
                        rainbow.print(f"1 ", color=color, end="")
                    else:
                        rainbow.print(f"  ", color=color, end="")
                
                if i < h - 1:  
                    print()
                """
                index = (index + 1) % 256
                
                strip.show()
                
                time.sleep(wait_ms * 1/1000)
            
def rgb_to_hex(color):
  """Converts an RGB color to a hexadecimal string.

  Args:
    r: The red component of the color, in the range 0-255.
    g: The green component of the color, in the range 0-255.
    b: The blue component of the color, in the range 0-255.

  Returns:
    A hexadecimal string representing the color, in the format #RRGGBB.
  """
  
  r, g, b = color

  return '#{:02x}{:02x}{:02x}'.format(r, g, b)
    
def wheel_tuple(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return (0, pos * 3, 255 - pos * 3)

def change_color(color, r, c):
    global color_cache

    color_cache[r][c] = color
    strip.setPixelColor(int(digit[r][c] - 1), color)

def changeColumn(strip, digit, wait_ms=50):
    h, w = digit.shape
    
    for i in range(w):
        column = digit[:, i]
        
        for index in column:
            if index != 0:
                print(f"Col {i} led: {index - 1}")
                strip.setPixelColor(int(index - 1), Color(255, 0, 0))
        
        strip.show()

        time.sleep(wait_ms * 2/1000)

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

def rainbow_(strip, wait_ms=20, iterations=1):
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

digit_indices = createDigit()
digit = np.zeros_like(digit_indices)
color_cache = [[0 for i in range(digit.shape[1])] for j in range(digit.shape[0])]
lock = threading.Lock()

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

t1 = threading.Thread(target=runDigit, args=(strip, 50))
t2 = threading.Thread(target=patterns, args=(strip, 50))

t1.start()
t2.start()

t1.join()
t2.join()

"""
# Main program logic follows:
if __name__ == '__main__':
    digit = createDigit()
    
    writeDigit(digit)
    changeColumn(strip, digit)
    
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    # Intialize the library (must be called once before other functions).
    strip.begin()

    print ('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')
        
    
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
"""