# This script controls a Gemma M0 as a replacement for the electronics
# inside a pedestal for displaying clear glass objects d'arte.

# Basic requirements for this script
# - dotStar LED will pulse, then pause for 15s off.
# - One key will control how the lights cycle - multicolor, single color, etc
# - One key will control how bright the lights pulse, from minimum, 25, 50, 75, maximum
# - Red LED will notify when keypress is detected
# - Pause rate is determined by chip temperature - 25s <70F, 15s at 80F, 5s at 90F

from digitalio import DigitalInOut, Direction, Pull
from touchio import TouchIn
import adafruit_dotstar as dotstar
import microcontroller
import board
import time

pulseTypes = {
  0:"MULTICOLOR",
  1:"BLUE",
  2:"", # g+b
  3:"GREEN",
  4:"", # r+g
  5:"WHITE", # r+g+b
  6:"", # r+b 
  7:"RED",
  }

cycle = 0 # Current location in the cycle
pulse = 0 # Current pulse choice.
delay = 15

# Built-in dotStar
bright = .01
dot = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=bright)

# Built-in red LED
led = DigitalInOut(board.D13)
led.direction = Direction.OUTPUT

# Capacitive touch
changePulse = TouchIn(board.A0)
changeBrightness = TouchIn(board.A2)

def updateDelay():
  # Get the chip temperature
  temp = microcontroller.cpu.temperature
  # Convert to F
  temp = temp * 9.0 / 5.0 + 32.0
  print("Temp: %0.1f" % temp)
  
  # Calculate our delay function
  newDelay = (80-temp) + 15
  if newDelay < 5:
   return 5
  if newDelay > 25:
   return 25
  return newDelay

while True:
  # Check temperature and update pulse rate
  delay = updateDelay()
  print("Delay: %0f" % delay)
  # Execute pulse program

  # Rest
  delayCount = delay - 1
  # This way there is a 1.5s delay before checking keys again
  time.sleep(1)
  while(delayCount > 0):
    time.sleep(.5)
    if changePulse.value:
      pulse = (pulse + 1) % (len(pulseTypes) - 1)
      print("New pulse: " + pulseTypes[pulse])
      # Exit the delay while loop and start the next pulse immediately
      break  
    if changeBrightness.value:
      bright = bright + .25
      if bright > 1.01:
        bright = 0.01
      print("Brightness: " + str(bright))
      # Exit the delay while loop and start the next pulse immediately
      break
    delayCount=delayCount-.5
