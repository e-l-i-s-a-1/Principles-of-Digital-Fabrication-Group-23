from machine import Pin
from servo import Servo
import utime

utime.sleep(1)

### led setup
led = Pin(5, Pin.OUT)
led.low() # initially OFF

### servo setup (with micropython-servo package)
## defaults: Servo(min_us=544.0, max_us=2400.0 ,min_deg=0.0, max_deg=180.0, freq=50)
servo = Servo(pin_id=16, min_us=1000.0, max_us=2000.0, min_deg=-90.0, max_deg=90.0, freq=50)
min_max_degs = (10.0, 80.0) # rotation range
delay = 0.025 # s
servo.write(min_max_degs[0]) # initial position min rotation

utime.sleep(1)

try:
    while True:
        led.high() # led ON
        print("on")
        i = servo.read() # returns the last set degs
        while i < min_max_degs[1]: # rotates servo +1deg at a time until max rotation
            i += 5
            servo.write(i)
            utime.sleep(delay)
        led.low() # led OFF
        print("off")
        utime.sleep(1)
        led.high() # led ON
        print("on")
        while i > min_max_degs[0]: # rotates servo -1deg at a time until min rotation
            i -= 5
            servo.write(i)
            utime.sleep(delay)
        led.low() # led OFF
        print("off")
        utime.sleep(1)
        
except KeyboardInterrupt:
    print("Stopping the program")
    led.low() # finally OFF
    servo.write(min_max_degs[0])
