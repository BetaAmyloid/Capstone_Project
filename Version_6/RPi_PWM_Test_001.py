import RPi.GPIO as GPIO
import time

# Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)

# Create PWM instance
pwm = GPIO.PWM(18, 1000)  # Pin 18, 1000 Hz frequency
pwm.start(0)  # Start PWM with 0% duty cycle

try:
    while True:
        for duty_cycle in range(0, 101, 1):  # Increase duty cycle from 0% to 100%
            pwm.ChangeDutyCycle(duty_cycle)
            time.sleep(0.05)
        for duty_cycle in range(100, -1, -1):  # Decrease duty cycle from 100% to 0%
            pwm.ChangeDutyCycle(duty_cycle)
            time.sleep(0.05)
except KeyboardInterrupt:
    pass

# Cleanup
pwm.stop()
GPIO.cleanup()
