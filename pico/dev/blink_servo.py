from machine import Pin, PWM
from servo import Servo
import utime

utime.sleep(1)

### general
min_value = 0
max_value = 65535

### led
led = Pin(28, Pin.OUT)
led.low() # initially OFF

### servo (pulse width range 500 - 2500 us ??)
# servo = PWM(Pin(16, Pin.OUT))
# servo_freq = 50 # Hz
# servo.freq(servo_freq)
# servo_period = 1 / servo_freq # s
# servo_min_pw = 1200 # us
# servo_max_pw = 1700 # us
# servo_min_duty = int((servo_min_pw * 1e-6 / servo_period) * max_value)
# servo_max_duty = int((servo_max_pw * 1e-6 / servo_period) * max_value)
# servo_step_duty = int((servo_min_duty + servo_max_duty) / 180)
# 
# servo.duty_u16(servo_min_duty) # initial position 0deg
# utime.sleep(1)
# 
# print("servo_min_duty = %d" % servo_min_duty)
# print("servo_max_duty = %d" % servo_max_duty)
# print("servo_step_duty = %d" % servo_step_duty)
# print()

### servo with micropython-servo
servo = Servo(16)
servo.write(45)
utime.sleep(1)

try:
    while True:
        led.high()
#         print("On")
        i = servo.read()
        while i < 135:
            i += 1
            servo.write(i)
            utime.sleep(0.025)
#         i = servo_min_duty
#         servo.duty_u16(i)
#         while i < servo_max_duty:
#             utime.sleep(0.1)
#             i = i + servo_step_duty
#             print(i)
#             servo.duty_u16(i)
        led.low()
#         print("Off")
        utime.sleep(1)
        led.high()
#         print("On")
        while i > 45:
            i -= 1
            servo.write(i)
            utime.sleep(0.025)
#         i = servo_max_duty
#         servo.duty_u16(i)
#         while i > servo_min_duty:
#             utime.sleep(0.1)
#             i = i - servo_step_duty
#             print(i)
#             servo.duty_u16(i)
        led.low()
#         print("Off")
        utime.sleep(1)
        
except KeyboardInterrupt:
    print("Stopping the program")
#     servo.deinit()
    led.low()
