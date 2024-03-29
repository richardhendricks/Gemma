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
  2:"AQUA", # g+b
  3:"GREEN",
  4:"YELLOW", # r+g
  5:"WHITE", # r+g+b
  6:"MAGENTA", # r+b 
  7:"RED",
  }

pulseColors = {
  0:[0x00,0x00,0x00], # BLACK - Because I am a doofus, I am doing this using Grey code
  1:[0x00,0x00,0xff], # BLUE
  2:[0x00,0xff,0xff], # AQUA
  3:[0x00,0xff,0x00], # GREEN
  4:[0xff,0xff,0x00], # YELLOW
  5:[0xff,0xff,0xff], # WHITE
  6:[0xff,0x00,0xff], # MAGENTA
  7:[0xff,0x00,0x00]  # RED
  }
cycle = 1 # Current location in the multicolor cycle
pulse = 0 # Current pulse choice.
RAMPTIME = 7.5 # Ramp up and down time, in seconds
STEP = 64 # Number of steps to ramp up/down
delay = 15

# Built-in dotStar
bright = 3

brightNess = { # Brightness on LEDs isn't linear, nor is the human eye.
  0:0.017,
  1:0.078,
  2:0.36,
  3:1.00
  }

dot = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=1)

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

def pulseLED(color):
  global cycle
  if (color == 0): # Multicolor, so cycle through all colors
    color = cycle
    cycle = (cycle + 1) % (len(pulseTypes))
    if color != 0:
      print("Pulsing Multicolor: " + pulseTypes[color])
    else:
      print("Pulsing Multicolor: BLACK")
  else:
    print("Pulsing: " + pulseTypes[pulse])
  # ramp upwards
  r=0
  g=0
  b=0
  rInc = pulseColors[color][0]*brightNess[bright]/STEP
  gInc = pulseColors[color][1]*brightNess[bright]/STEP
  bInc = pulseColors[color][2]*brightNess[bright]/STEP
  count = 0
  print("Ramp UP")
  while (count < STEP):
    dot[0]=int(r), int(g), int(b)
    dot.show()
    r = r + rInc
    g = g + gInc
    b = b + bInc
    count = count + 1
    time.sleep(RAMPTIME/STEP)
  print("Pause at max")
  time.sleep(RAMPTIME/3.75) # Nominally 2s
  print("Ramp DOWN")
  while (count > -1):
    dot[0]=int(r), int(g), int(b)
    dot.show()
    r = r - rInc
    g = g - gInc
    b = b - bInc
    count = count - 1
    time.sleep(RAMPTIME/STEP)
    
    
while True:
  # Check temperature and update pulse rate
  delay = updateDelay()
  print("Delay: %0f" % delay)
  # Execute pulse program
  pulseLED(pulse)
  print("Rest")
  delayCount = delay - 1
  # This way there is a 1s delay before checking keys again
  time.sleep(.5)
  while(delayCount > 0):
    time.sleep(.5)
    if changePulse.value:
      pulse = (pulse + 1) % (len(pulseTypes))
      print("New pulse: " + pulseTypes[pulse])
      # Exit the delay while loop and start the next pulse immediately
      break  
    if changeBrightness.value:
      bright = (bright + 1) %(len(brightNess))
      print("Brightness: " + str(brightNess[bright]))
      # Exit the delay while loop and start the next pulse immediately
      break
    delayCount=delayCount-.5
