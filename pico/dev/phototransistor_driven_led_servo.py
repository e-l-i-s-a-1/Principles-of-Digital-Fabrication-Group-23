from machine import Pin, ADC
from servo import Servo
import utime

utime.sleep(1)

### pico ADC range
min_max_value = (0, 65535)

### phototransistor setup
sensor = ADC(26) # A0
threshold = int(0.6 * (min_max_value[1] - min_max_value[0]))

### led setup
led = Pin(5, Pin.OUT)
led.low() # initially OFF

### servo setup (with micropython-servo package)
## defaults: Servo(min_us=544.0, max_us=2400.0 ,min_deg=0.0, max_deg=180.0, freq=50)
servo = Servo(pin_id=16, min_us=1000.0, max_us=2000.0, min_deg=-90.0, max_deg=90.0, freq=50)
min_max_degs = (-80.0, 80.0) # rotation range
delay = 0.005 # s
servo.write(min_max_degs[0]) # initial position min rotation

utime.sleep(1)

try:
    while True:
        light = sensor.read_u16()
        print("light = %d" % light)
        if light > threshold:
            print("things happen")
            led.high() # led ON
            i = servo.read() # returns the last set degs
            while i < min_max_degs[1]: # rotates servo +1deg at a time until max rotation
                i += 5
                servo.write(i)
                utime.sleep(delay)
            utime.sleep(0.5)
            while i > min_max_degs[0]: # rotates servo -1deg at a time until min rotation
                i -= 5
                servo.write(i)
                utime.sleep(delay)
        else:
            led.low() # led OFF
            servo.write(min_max_degs[0])
        utime.sleep(0.5)
        
except KeyboardInterrupt:
    print("Stopping the program")
    led.low() # finally OFF
    servo.write(min_max_degs[0]) # finally min rotation
    utime.sleep(1)
