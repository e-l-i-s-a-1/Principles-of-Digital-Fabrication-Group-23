from machine import Pin, ADC, PWM
from servo import Servo
import utime
import _thread

utime.sleep(1)

class Shared:
    min_max_value = (0, 65535) # pico u16 range
    sample_delay = 0.25 # delay for tuning overall response [s]
    
    ### servo setup (with micropython-servo package)
    ## defaults: Servo(min_us=544.0, max_us=2400.0 ,min_deg=0.0, max_deg=180.0, freq=50)
    servo = Servo(pin_id=16, min_us=1000.0, max_us=2000.0, min_deg=-90.0, max_deg=90.0, freq=50)
    min_max_degs = (-80.0, 80.0) # rotation range [deg]
    servo_delay = 0.005 # delay between 5deg rotation [s]
    servo.write(min_max_degs[0]) # initial position min rotation
    
    ### phototransistor setup
    sensor_L = ADC(26) # A0 (left sensor)
    sensor_R = ADC(27) # A1 (right sensor)
    th_value = 0.6 # threshold value [0.0, 1.0] for sensitivity
    # checking accepted limits
    if th_value > 1.0:
        th_value = 1.0
    elif th_value < 0.0:
        th_value = 0.0
    # scaling threshold to u16
    threshold = int(th_value * (min_max_value[1] - min_max_value[0]))
    
    @classmethod
    def read_sensor_L(cls):
        # reads the u16 value from the left phototransistor
        return cls.sensor_L.read_u16()
    
    @classmethod
    def read_sensor_R(cls):
        # reads the u16 value from the right phototransistor
        return cls.sensor_R.read_u16()
    
    @classmethod
    def read_servo(cls):
        # returns the last set degs from the servo
        return cls.servo.read()
    
    @classmethod
    def write_servo(cls, deg):
        # sets degrees to servo
        cls.servo.write(deg)

def servo_thread():
    try:
        while True:
            # if enough light is sensed at any sensor, the servo rotates once back and forth
            light_L = Shared.read_sensor_L()
            light_R = Shared.read_sensor_R()
            print("light_L = %d" % light_L)
            print("light_R = %d" % light_R)
            max_light = max(light_L, light_R)
            if max_light >= Shared.threshold:
                i = Shared.read_servo()
                while i < Shared.min_max_degs[1]: # rotates servo +5deg at a time until max rotation
                    i += 5
                    Shared.write_servo(i)
                    utime.sleep(Shared.servo_delay)
                while i > Shared.min_max_degs[0]: # rotates servo -5deg at a time until min rotation
                    i -= 5
                    Shared.write_servo(i)
                    utime.sleep(Shared.servo_delay)
            utime.sleep(Shared.sample_delay)
    
    except KeyboardInterrupt:
        print("Stopping the program")
        Shared.write_servo(Shared.min_max_degs[0]) # finally min rotation
        utime.sleep(1)

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

utime.sleep(1)

### start servo thread on core 1
_thread.start_new_thread(servo_thread, ())

### main thread on core 0
try:
    while True:
        # if enough light sensed at left sensor, right motor rotates (and vice versa)
        # motor speed is based on the intensity of the light
        light_L = Shared.read_sensor_L()
        light_R = Shared.read_sensor_R()
        if light_L >= Shared.threshold:
            motor_R.duty_u16(int(speed_factor * light_L))
        else:
            motor_R.duty_u16(0)
        if light_R >= threshold:
            motor_L.duty_u16(int(speed_factor * light_R))
        else:
            motor_L.duty_u16(0)
        utime.sleep(Shared.sample_delay)
        
except KeyboardInterrupt:
    motor_L.duty_u16(0)
    motor_R.duty_u16(0)
    utime.sleep(1)
