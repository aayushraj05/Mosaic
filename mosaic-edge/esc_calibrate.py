# esc_calibrate.py
# Run ONCE before first motor test
# Teaches ESCs the throttle range
# Propellers must be OFF

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

ESC_PINS = [
    config.MOTOR_GPIO_FL,
    config.MOTOR_GPIO_FR,
    config.MOTOR_GPIO_RL,
    config.MOTOR_GPIO_RR
]
PWM_FREQ = config.ESC_PWM_FREQ


def us_to_duty(us):
    return (us / 20000.0) * 100.0


print("\n" + "="*50)
print("ESC CALIBRATION")
print("Avionics C2826 1000KV on F450")
print("="*50)
print()
print("CHECKLIST:")
print("All 4 propellers removed")
print("Keithley set to 11V 3A")
print("Keithley OUTPUT is currently OFF")
print("ESC signal wires connected to Pi")
print("ESC GND wires connected to Pi GND")
print()
confirm = input(
    "All items checked? Type YES: ")
if confirm.upper() != 'YES':
    print("Aborted. Check all items first.")
    exit()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

pwms = []
for pin in ESC_PINS:
    GPIO.setup(pin, GPIO.OUT)
    p = GPIO.PWM(pin, PWM_FREQ)
    p.start(0)
    pwms.append(p)

print("\n--- STEP 1 ---")
print("Sending MAX signal to all ESCs")
print("(2000 microseconds)")
for p in pwms:
    p.ChangeDutyCycle(us_to_duty(2000))

print()
print("NOW turn Keithley OUTPUT ON")
print("ESCs will power up")
print("Listen for startup beeps...")
print("Wait 4 seconds after beeps...")
input("Press ENTER after ESCs beep startup...")

print("\n--- STEP 2 ---")
print("Sending MIN signal to all ESCs")
print("(1000 microseconds)")
for p in pwms:
    p.ChangeDutyCycle(us_to_duty(1000))

print()
print("Listen for confirmation beeps...")
print("Usually 2 short beeps = calibrated")
time.sleep(3)

print("\n--- STEP 3 ---")
print("Sending ARM signal")
print("(1050 microseconds)")
for p in pwms:
    p.ChangeDutyCycle(us_to_duty(1050))
time.sleep(2)

print("Calibration complete")
print("ESCs now know:")
print("  1000us = stop")
print("  2000us = full throttle")
print()
print("You can now run motor_controller.py")

for p in pwms:
    p.stop()
GPIO.cleanup()
print("Done")
