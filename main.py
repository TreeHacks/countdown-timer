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
    """
    Print the given array to the console.

    Args:
        array (np.array): The array to print.
    """
    
    shape = array.shape
    
    for i in range(shape[0]):
        for j in range(shape[1]):
            print(array[i][j], end=" ")
        print()
        
def runDigit():
    """
    Run the digit on the LED strip. This function will update the digit to display the current time
    and then write the digit to the LED strip.
    """
    
    global digit
    global strip
    
    while True:
        now = datetime.now()
        current_time = now.strftime("%H%M%S")
        # print("Current Time =", current_time)

        updateDigit(current_time)
        
        #printArray(digit)
        
        #for i in range(digit.shape[0]):
        #    for j in range(digit.shape[1]):
        #        strip.setPixelColor(int(digit[i][j]), Color(255, 0, 0))
        
        #strip.show()

        time.sleep(0.05)

def createDigit(start_index=1, w=37, h=75):
    """
    Create a sparse matrix of indices that represent a digit on the LED strip. A 0 
    means there's no LED at that position, and a positive integer represents the
    index of the LED on the strip. 
    
    NOTE: The indices are 1-indexed, so the first index is 1, not 0. This is to
    avoid confusion with 0 being no LED.

    Args:
        start_index (int, optional): The starting index for the LED strip. Defaults to 1.
        w (int, optional): The width of the digit. 
        h (int, optional): The height of the digit.
        
    Returns:
        np.array: A sparse matrix of indices representing the digit.
    """
    
    new_digit = np.zeros((h, w), dtype=int)
    index = start_index
        
    # Across to right
    for i in range(w - 2):
        new_digit[h//2][i + 1] = index
        index += 1
        
    # Up to top right
    for i in range(h//2 + 1):
        new_digit[h//2 - i][w - 1] = index
        index += 1
        
    # Across to left
    for i in range(w - 2):
        new_digit[0][w - i - 2] = index
        index += 1
        
    # Down to bottom left
    for i in range(h):
        new_digit[i][0] = index
        index += 1
        
    # Across to right
    for i in range(w - 2):
        new_digit[h - 1][i + 1] = index
        index += 1
        
    # Up to middle right
    for i in range(math.ceil(h/2 - 1)):
        new_digit[h - 1 - i][w - 1] = index
        index += 1
    
    return new_digit

def writeDigit(digit_index, number):
    """
    For a given digit, write the number to the digit mask. The number is written
    by turning on the LEDs that are part of the number and turning off the LEDs
    that are not part of the number. This is done by creating a mask of 1s and 0s
    and then using the mask to turn on and off the LEDs.
    
    Args:
        digit_index (int): The index of the digit to write to.
        number (int): The number to write to the digit.
        
    """
    
    global digit
    global color_cache
    global digit_indices
    
    h, w = digit[digit_index].shape
    
    """
    Numpy slice objects for the different parts of the digit - the LEDs start in the middle 
    and to the right, and then go counter-clockwise around the digit
    """
    middle = np.s_[h//2, 1:w-1]
    right_top = np.s_[:h//2 + 1, w-1]
    top = np.s_[0, 1:w - 1]
    left_top = np.s_[:h//2 + 1, 0]
    left_bottom = np.s_[h//2 + 1:, 0]
    bottom = np.s_[h - 1, 1:w - 1]
    right_bottom = np.s_[h//2 + 1:, w-1]
    
    mask = np.zeros((h, w), dtype=int)
    
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
    
    # Get the indices of the LEDs that are part of the digit
    digit[digit_index] = np.where(mask, digit_indices[digit_index], 0)
    
    # Turn on the LEDs that are part of the digit (should be on)
    for r in range(h):
        for c in range(w):
            if digit[digit_index][r][c] != 0:
                cached = color_cache[r][c]
                if cached != 0:
                    strip.setPixelColor(int(digit[digit_index][r][c] - 1), cached)

    # Create the anti-digit that gets the leds that are not part of the digit (should be off)
    anti_digit = np.where(mask, 0, digit_indices[digit_index])

    # Turn off the LEDs that are not part of the digit
    for r in range(h):
        for c in range(w):
            if digit[digit_index][r][c] == 0:
                strip.setPixelColor(int(anti_digit[r][c] - 1), Color(0, 0, 0))

    strip.show()
    
def updateDigit(current_time):
    """
    Given the current time, update all the digits to display the current time. This is done
    by writing each digit to the LED strip.
    
    Args:
        current_time (str): The current time in the format HHMMSS.
    """
    
    global lock
    global digit
    global digit_indices
    global color_cache
    
    lock.acquire() # Lock the thread so that the digit can be updated (mainly to stop patterns from updating the digit at the same time)
    
    for i in range(len(digit)):
        writeDigit(i, int(current_time[i]))
     
    lock.release() # Release the lock so that the digit can be updated by another thread

def patterns(wait_ms=50):
    """
    Run the patterns on the LED strip. This function will run the patterns on the LED strip
    and update the digit to display the current time.
    """
    
    global digit
    global strip
     
    n, h, w = digit.shape # Number of digits, height, width
    
    while True:
        # Rainbow
        rainbow(wait_ms)
            
def rainbow(wait_ms=50):
    global digit
    global strip
    
    for j in range(256): # One cycle of all 256 colors in the wheel
        height_arr = list(range(h))
                
        for r in height_arr:
            strip_color = wheel((r + j) & 255) # Get the color for the row (shifted by j to make it move)
            
            for digit_index in range(n):
                for c in range(w):
                    change_color(strip_color, digit_index, r, c)
                
            strip.show() # Show the changes to the strip
            
            time.sleep(wait_ms/1000) # Wait for a bit before moving to the next row
            
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
    
def change_color(color, n, r, c):
    """
    Change the color of the LED at the given position

    Args:
        color (Color): The color to change the LED to (RGB)
        n (int): The digit index
        r (int): The row index
        c (int): The column index
    """

    global color_cache
    global digit

    color_cache[n][r][c] = color
    strip.setPixelColor(int(digit[n][r][c] - 1), color)

def wheel(pos, use_tuple=False):
    """
    Generate rainbow colors across 0-255 positions.
    
    Args:
        pos (int): The position in the rainbow.
        use_tuple (bool): Toggle the return of Color or tuple.
        
    Returns:
        Color or tuple: The color at the given position.
    """
    
    if pos < 85:
        color = (pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        color = (255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        color = (0, pos * 3, 255 - pos * 3)

    if use_tuple:
        return color
    else:
        return Color(*color)
        
def changeColumn(strip, digit, wait_ms=50):
    h, w = digit.shape
    
    for i in range(w):
        column = digit[:, i]
        
        for index in column:
            if index != 0:
                print(f"Col {i} led: {index - 1}")
                strip.setPixelColor(int(index - 1), Color(255, 0, 0))
        
        strip.show()

        time.sleep(wait_ms/1000)

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

num_digits = 6

digit_indices = [createDigit(1 + i * 300) for i in range(num_digits)]
digit_indices = np.array(digit_indices)
digit = np.zeros_like(digit_indices)

color_cache = [[[0] * digit.shape[1] for i in range(digit.shape[0])] for j in range(num_digits)]

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

lock = threading.Lock()

t1 = threading.Thread(target=runDigit, args=(50))
t2 = threading.Thread(target=patterns, args=(50))

t1.start()
t2.start()

t1.join()
t2.join()
