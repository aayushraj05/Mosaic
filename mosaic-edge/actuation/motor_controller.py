# motor_controller.py
# F450 brushless motor control via ESC
# Avionics C2826 1000KV
# PWM signal: 50Hz, 1000-2000 microseconds

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

# GPIO pins from config
ESC_FL   = config.MOTOR_GPIO_FL
ESC_FR   = config.MOTOR_GPIO_FR
ESC_RL   = config.MOTOR_GPIO_RL
ESC_RR   = config.MOTOR_GPIO_RR
ESC_PINS = [ESC_FL, ESC_FR, ESC_RL, ESC_RR]

ESC_NAMES = {
    ESC_FL: 'Front Left',
    ESC_FR: 'Front Right',
    ESC_RL: 'Rear Left',
    ESC_RR: 'Rear Right'
}

# Throttle values
ESC_MIN      = config.ESC_MIN_US
ESC_ARM      = config.ESC_ARM_US
ESC_IDLE     = config.ESC_IDLE_US
BENCH_MAX    = config.BENCH_SAFE_MAX
PWM_FREQ     = config.ESC_PWM_FREQ


class MotorController:
    def __init__(self):
        print("="*40)
        print("MOSAIC Motor Controller")
        print("F450 Avionics C2826 1000KV")
        print("="*40)

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        self.pwm_objects = {}
        self.armed       = False

        for pin in ESC_PINS:
            GPIO.setup(pin, GPIO.OUT)
            pwm = GPIO.PWM(pin, PWM_FREQ)
            pwm.start(0)
            self.pwm_objects[pin] = pwm
            print(
                f"  ESC {ESC_NAMES[pin]}"
                f" GPIO{pin} ready")

        print("Arming ESCs...")
        self._arm()
        print("Motors ready\n")

    def _us_to_duty(self, us):
        return (us / 20000.0) * 100.0

    def _set_pin(self, pin, us):
        # Hard cap — never above BENCH_MAX
        # Change BENCH_SAFE_MAX in config.py
        # to 2000 only when using LiPo
        us = max(ESC_MIN, min(BENCH_MAX, us))
        self.pwm_objects[pin].ChangeDutyCycle(
            self._us_to_duty(us))

    def _set_all(self, us):
        for pin in ESC_PINS:
            self._set_pin(pin, us)

    def _arm(self):
        self._set_all(ESC_MIN)
        time.sleep(3)
        self.armed = True

    def stop(self):
        self._set_all(ESC_MIN)
        print("Motors stopped")

    def confirmation_spin(self):
        # Called when victim CONFIRMED
        if not self.armed:
            print("Motors not armed")
            return
        print("ACTUATION: Confirmation spin")
        # Slow ramp up
        for us in range(
                ESC_MIN, ESC_IDLE + 1, 5):
            self._set_all(us)
            time.sleep(0.01)
        # Hold 2 seconds
        time.sleep(2)
        # Slow ramp down
        for us in range(
                ESC_IDLE, ESC_MIN - 1, -5):
            self._set_all(us)
            time.sleep(0.01)
        self._set_all(ESC_MIN)
        print("Confirmation spin done\n")

    def alert_pulse(self):
        # Called when CRITICAL victim
        # 3 short pulses
        if not self.armed:
            return
        print("ACTUATION: Alert pulse CRITICAL")
        for i in range(3):
            self._set_all(ESC_IDLE)
            time.sleep(0.3)
            self._set_all(ESC_MIN)
            time.sleep(0.2)
        print("Alert pulse done\n")

    def rescan_pulse(self):
        # Called when threshold updated
        if not self.armed:
            return
        print("ACTUATION: Rescan pulse")
        self._set_all(ESC_IDLE)
        time.sleep(0.5)
        self._set_all(ESC_MIN)
        print("Rescan pulse done\n")

    def test_individual(self):
        print("Testing each motor 1 second...")
        for pin in ESC_PINS:
            print(f"  {ESC_NAMES[pin]}...")
            self._set_pin(pin, ESC_IDLE)
            time.sleep(1)
            self._set_pin(pin, ESC_MIN)
            time.sleep(0.5)
            print(f"  {ESC_NAMES[pin]} OK")
        print("Individual test done\n")

    def test_all(self):
        print("All motors spinning 2 seconds...")
        self._set_all(ESC_IDLE)
        time.sleep(2)
        self._set_all(ESC_MIN)
        print("All motors test done\n")

    def cleanup(self):
        self.stop()
        time.sleep(0.5)
        for pwm in self.pwm_objects.values():
            pwm.stop()
        GPIO.cleanup()
        print("Motor controller cleaned up")


# ─────────────────────────────────────────
# STANDALONE TEST MENU
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*50)
    print("F450 MOTOR TEST MENU")
    print("="*50)
    print()
    print("SAFETY CHECKLIST:")
    print("All 4 propellers REMOVED")
    print("ESC signal wires connected to Pi")
    print("Common GND connected")
    print("Keithley 11V 3A OUTPUT ON")
    print("Pi powered from USB-C separately")
    print("ESC calibration done already")
    print()

    go = input("Type YES to continue: ")
    if go.upper() != 'YES':
        print("Aborted")
        exit()

    m = MotorController()

    while True:
        print("Start"*40)
        print("1 All motors test")
        print("2 Individual motors test")
        print("3 Confirmation spin (MOSAIC)")
        print("4 Alert pulse (MOSAIC)")
        print("5 Rescan pulse (MOSAIC)")
        print("q Quit")
        print("Done"*40)

        choice = input("Choice: ").strip()

        if choice == '1':
            m.test_all()
        elif choice == '2':
            m.test_individual()
        elif choice == '3':
            m.confirmation_spin()
        elif choice == '4':
            m.alert_pulse()
        elif choice == '5':
            m.rescan_pulse()
        elif choice.lower() == 'q':
            break
        else:
            print("Invalid")

    m.cleanup()
