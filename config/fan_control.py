import RPi.GPIO as GPIO
import time

fan_pin = 12
GPIO.setmode(GPIO.BOARD)
GPIO.setup(fan_pin, GPIO.OUT)

pi_pwm = GPIO.PWM(fan_pin, 100)
pi_pwm.start(0)
pi_pwm.ChangeDutyCycle(100)
while True:
  time.sleep(1)