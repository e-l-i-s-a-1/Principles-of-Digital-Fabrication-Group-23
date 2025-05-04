from machine import Pin, ADC, PWM
from servo import Servo
import utime

# !!! save as main.py to pico !!!

utime.sleep(1)

debug = False # boolean for debug prints

led = Pin("LED", Pin.OUT) # built-in led to indicate power ON & READY

min_max_value = (0, 65535) # pico uint16 range
sample_delay = 0.15 # delay between cycles [s] # TUNING PARAMETER

### phototransistor setup
sensor_L = ADC(26) # A0 (left sensor)
sensor_R = ADC(27) # A1 (right sensor)
# checking the ambient light level and setting the light threshold
print("Sensing the illuminance level of the current surroundings...")
light_values = []
for i in range(10):
    light_L = sensor_L.read_u16()
    light_R = sensor_R.read_u16()
    light_values.append((light_L + light_R) / 2)
    utime.sleep(sample_delay * 2)
threshold = sum(light_values) / len(light_values)
init_threshold_factor = 1.5 # TUNING PARAMETER
threshold = int(init_threshold_factor * threshold)
init_threshold = threshold # save the initial threshold
print("initial threshold: %d" % threshold)

### motors setup
motor_L = PWM(Pin(15))
motor_R = PWM(Pin(10))
motor_L.freq(50) # [Hz]
motor_R.freq(50) # [Hz]
# minimum value for motor speed (45680 to get the minimum 2.3V)
speed_transfer = 50000 # TUNING PARAMETER
# scale factor for scaling light values to motor speed
speed_factor = round((min_max_value[1] - speed_transfer) / min_max_value[1], 2)
# check limits (speed factor = [0.0, 1.0])
speed_factor = max(0.0, speed_factor)
speed_factor = min(1.0, speed_factor)
print("speed_factor: %.2f" % speed_factor)
print("-> speed range: %d - %d" % (int(speed_transfer + speed_factor * min_max_value[0]),
                                   min(int(speed_transfer + speed_factor * min_max_value[1]), min_max_value[1])))

### servo setup (with micropython-servo package)
## defaults: Servo(min_us=544.0, max_us=2400.0 ,min_deg=0.0, max_deg=180.0, freq=50)
servo = Servo(pin_id=16, min_us=1000.0, max_us=2000.0, min_deg=-90.0, max_deg=90.0, freq=50)
min_max_degs = (-70.0, 70.0) # rotation range [deg] # TUNING PARAMETER
servo_inc = 3 # rotation increment [deg] # TUNING PARAMETER
servo_delay = 0.005 # delay between rotation increments [s] # TUNING PARAMETER
servo.write(min_max_degs[0]) # initial position min rotation

utime.sleep(1)

led.value(True) # led ON

try:
    while True:
        i = servo.read() # returns the last set degs
        
        # read light level on bot sides
        light_L = sensor_L.read_u16()
        light_R = sensor_R.read_u16()
        if debug:
            print("light_L = %d" % light_L)
            print("light_R = %d" % light_R)
        
        # update running average of the light level
        tmp_light_values = light_values[:-1]
        light_values = [(light_L + light_R) / 2]
        light_values.extend(tmp_light_values)
        light_value = int(sum(light_values) / len(light_values))
        
        # modify threshold if current conditions (running average) has changed enough
        if abs(light_value - threshold) > 5000:
            threshold = max(light_value, init_threshold)
            if debug:
                print("threshold changed to: %d" % threshold)
        
        # run motors if light level is over current threshold
#         max_light = max(light_L, light_R)
#         if max_light >= threshold:
        if light_L >= threshold:
            motor_R_speed = int(speed_transfer + speed_factor * light_L)
            motor_R.duty_u16(min(motor_R_speed, min_max_value[1]))
        else:
            motor_R.duty_u16(0)
        if light_R >= threshold:
            motor_L_speed = int(speed_transfer + speed_factor * light_R)
            motor_L.duty_u16(min(motor_L_speed, min_max_value[1]))
        else:
            motor_L.duty_u16(0)
#         else:
#             motor_L.duty_u16(0)
#             motor_R.duty_u16(0)
        
        # swing hammer if light level is over initial threshold
        max_light = max(light_L, light_R)
        if max_light >= init_threshold:
            while i < min_max_degs[1]: # rotates servo +increment at a time until max rotation
                i += servo_inc
                servo.write(i)
                utime.sleep(servo_delay)
            while i > min_max_degs[0]: # rotates servo -increment at a time until min rotation
                i -= servo_inc
                servo.write(i)
                utime.sleep(servo_delay)
        else:
            if i != min_max_degs[0]:
                servo.write(min_max_degs[0])

        # short pause before the next cycle
        utime.sleep(sample_delay)
        
except KeyboardInterrupt:
    print("Stopping the program")
    led.value(False) # led OFF
    servo.write(min_max_degs[0]) # finally min rotation
    motor_L.duty_u16(0) # stop motors
    motor_R.duty_u16(0)
    utime.sleep(1)
