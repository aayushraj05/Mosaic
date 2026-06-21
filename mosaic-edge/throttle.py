# throttle_test.py
# Manually test throttle levels
# Find minimum throttle that spins motor
# Use ONE motor at a time with bench supply

import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS']      = '1'

import RPi.GPIO as GPIO
import time
import sys
sys.path.insert(
    0,
    '/home/leopardtech/Desktop/mosaic-edge')
import config

# Test ONE pin at a time
# Change this to test different motor
TEST_PIN  = config.MOTOR_GPIO_FL
TEST_NAME = "Front Left"

PWM_FREQ  = 50

def us_to_duty(us):
    return (us / 20000.0) * 100.0

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(TEST_PIN, GPIO.OUT)
p = GPIO.PWM(TEST_PIN, PWM_FREQ)
p.start(0)

print("\n" + "="*50)
print(f"THROTTLE TEST : {TEST_NAME}")
print(f"GPIO: {TEST_PIN}")
print("="*50)
print()
print("Arming ESC (3 seconds)...")
p.ChangeDutyCycle(us_to_duty(1000))
time.sleep(3)
print("Armed\n")

print("Commands:")
print("  Number = set throttle (1000-1500)")
print("  s      = stop motor")
print("  q      = quit")
print()
print("Start with 1150")
print("Increase by 50 each time")
print("Stop when motor spins")
print("Note the minimum throttle value")
print()

while True:
    cmd = input(
        "Enter throttle us (1000-1500): "
    ).strip()

    if cmd.lower() == 'q':
        break
    elif cmd.lower() == 's':
        p.ChangeDutyCycle(us_to_duty(1000))
        print("Stopped\n")
    else:
        try:
            us = int(cmd)
            # Hard cap at 1500 for bench safety
            if us > 1500:
                print("Max 1500 on bench supply")
                us = 1500
            if us < 1000:
                us = 1000
            print(f"Setting {us}us...")
            p.ChangeDutyCycle(
                us_to_duty(us))
            time.sleep(0.5)
        except ValueError:
            print("Enter a number")

p.ChangeDutyCycle(us_to_duty(1000))
time.sleep(0.5)
p.stop()
GPIO.cleanup()
print("Done")
