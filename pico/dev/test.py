from machine import Pin
import time

# LED pin GP9
LED = Pin(9, Pin.OUT)

while True:
    LED.value(1) # LED on
    time.sleep(2) # wait 2s
    LED.value(0) # LED off
    time.sleep(2) # wait 2s
