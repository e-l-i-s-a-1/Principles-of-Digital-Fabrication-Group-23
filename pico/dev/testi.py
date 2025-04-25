from machine import Pin, ADC, PWM
from servo import Servo
import utime

utime.sleep(1)

min_max_value = (0, 65535) # pico u16 range
sample_delay = 0.25 # delay for tuning overall response [s]

### phototransistor setup
sensor_L = ADC(26) # A0 (left sensor)
sensor_R = ADC(27) # A1 (right sensor)
th_value = 0.8 # threshold value [0.0, 1.0] for sensitivity

# checking accepted limits
# scaling threshold to u16
if th_value > 1.0:
    th_value = 1.0
elif th_value < 0.0:
    th_value = 0.0
threshold = int(th_value * (min_max_value[1] - min_max_value[0]))

### motors setup
motor_L = PWM(Pin(15))
motor_R = PWM(Pin(10))
motor_L.freq(50) # [Hz]
motor_R.freq(50) # [Hz]
speed_factor = 0.5 # scale factor for motor speed tuning [0.0, 1.0]

# checking accepted limits
if speed_factor > 1.0:
    speed_factor = 1.0
elif speed_factor < 0.0:
    speed_factor = 0.0

### servo setup (with micropython-servo package)
## defaults: Servo(min_us=544.0, max_us=2400.0 ,min_deg=0.0, max_deg=180.0, freq=50)
servo = Servo(pin_id=16, min_us=1000.0, max_us=2000.0, min_deg=-90.0, max_deg=90.0, freq=50)
min_max_degs = (-70.0, 70.0) # rotation range [deg]
servo_delay = 0.005 # delay between 5deg rotation [s]
servo.write(min_max_degs[0]) # initial position min rotation

utime.sleep(1)

try:
    while True:
        i = servo.read() # returns the last set degs
        light_L = sensor_L.read_u16()
        light_R = sensor_R.read_u16()
        print("light_L = %d" % light_L)
        print("light_R = %d" % light_R)
        max_light = max(light_L, light_R)
        if max_light >= threshold:
            if light_L >= threshold:
                motor_R.duty_u16(int(speed_factor * light_L))
            else:
                motor_R.duty_u16(0)
            if light_R >= threshold:
                motor_L.duty_u16(int(speed_factor * light_R))
            else:
                motor_L.duty_u16(0)
            while i < min_max_degs[1]: # rotates servo +1deg at a time until max rotation
                i += 5
                servo.write(i)
                utime.sleep(servo_delay)
            while i > min_max_degs[0]: # rotates servo -1deg at a time until min rotation
                i -= 5
                servo.write(i)
                utime.sleep(servo_delay)
        else:
            if i != min_max_degs[0]:
                servo.write(min_max_degs[0])
            motor_L.duty_u16(0)
            motor_R.duty_u16(0)
        utime.sleep(sample_delay)
        
except KeyboardInterrupt:
    print("Stopping the program")
    servo.write(min_max_degs[0]) # finally min rotation
    motor_L.duty_u16(0)
    motor_R.duty_u16(0)
    utime.sleep(1)
