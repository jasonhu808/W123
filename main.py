import time
import ina219
import idledash
import os
import threading
import psutil
import tkinter as tk
import RPi.GPIO as GPIO
from collections import deque


if os.environ.get('DISPLAY', '') == '':
    print('no display found. Using :0.0')
    os.environ.__setitem__('DISPLAY', ':0.0')


## Definitions
mainstate = "init"
ina1 = ina219.INA219(addr=0x40) ## Battery Voltage
ina2 = ina219.INA219(addr=0x41)
ina3 = ina219.INA219(addr=0x42) ## Reverse 
ina4 = ina219.INA219(addr=0x43)
flag1 = False
flag2 = False
camera_started = False
flag_reverse = False

direction = 1  # 1 for increasing, -1 for decreasing
max_rpm = 4500
increment = 10  # Change this value to adjust the speed of the sweep
rpm = 0

battV = 0.0  # Initialize global variables
coolV = 0.0
coolF = 0.0
last_update_time = 0
start_t = 0

# Setup GPIO for RPM
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP)

PULSES_PER_REV = 4
GEAR_RATIO = 6.25 / 2.5  # 2.5
rpm_history = deque(maxlen=15)
pulse_count = 0
last_time = time.time()

thread1 = idledash.idledash()

def get_cpu_temp():
    temps = psutil.sensors_temperatures()
    cpu_temp = temps.get('cpu_thermal', [])
    if cpu_temp:
        return cpu_temp[0].current
    else:
        return None

def coolantVtoF(coolV):
    coolF = (coolV / 5) * 212
    return round(coolF, 1)

# def update_rpm():
#     global rpm, direction
#     while True:
#         rpm += direction * increment
#         if rpm >= max_rpm or rpm <= 0:
#             direction *= -1 
#         time.sleep(0.01)

# def pulse_callback(channel):
#     global pulse_count
#     pulse_count += 1

# GPIO.add_event_detect(17, GPIO.FALLING, callback=pulse_callback, bouncetime=1)

def pulse_callback(channel):
    global pulse_count
    pulse_count += 1

GPIO.add_event_detect(17, GPIO.FALLING, callback=pulse_callback, bouncetime=1)

# Correct update_rpm function
def update_rpm():
    global rpm, pulse_count, last_time
    UPDATE_INTERVAL = 0.05  # seconds

    while True:
        current_time = time.time()
        elapsed_time = current_time - last_time

        if elapsed_time >= UPDATE_INTERVAL:
            revolutions = pulse_count / PULSES_PER_REV
            rpm_measured = (revolutions * 60) / elapsed_time
            rpm_corrected = rpm_measured / GEAR_RATIO

            rpm_history.append(rpm_corrected)
            rpm = sum(rpm_history) / len(rpm_history)

            pulse_count = 0
            last_time = current_time

        time.sleep(0.005)

# def update_rpm():
#     global rpm, pulse_count, last_time
#     UPDATE_INTERVAL = 0.1  # seconds

#     while True:
#         current_time = time.time()
#         elapsed_time = current_time - last_time

#         if elapsed_time >= UPDATE_INTERVAL:
#             revolutions = pulse_count / PULSES_PER_REV
#             rpm_measured = (revolutions * 60) / elapsed_time
#             rpm_corrected = rpm_measured / GEAR_RATIO

#             # Smooth with moving average
#             rpm_history.append(rpm_corrected)
#             rpm = sum(rpm_history) / len(rpm_history)

#             # Reset for next window
#             pulse_count = 0
#             last_time = current_time
        
#         time.sleep(0.005)

def read_sensors():
    global battV, coolV, coolF
    while True:
        battV = round(ina1.getBusVoltage_V(), 2)
        coolV = ina2.getBusVoltage_V()
        coolF = coolantVtoF(coolV)
        time.sleep(0.2)

def update_idle(current_time):
    global last_update_time
    thread1.update_tach(rpm)
    if (rpm > 2000) and (rpm < 2500):
        thread1.show_shift("yellow")
    elif (rpm > 2500):
        thread1.show_shift("red")
    else:
        thread1.show_shift("black")

    # Only update these values once per second
    if current_time - last_update_time >= 1.0:
        thread1.update_idletasks()
        thread1.update_class()
        thread1.update_batt_v(battV)
        # thread1.update_cool_f(get_cpu_temp())
        thread1.update_cpu_t(round(get_cpu_temp(), 1))
        last_update_time = current_time  # Reset the timer
        return

# Start the RPM update in a separate thread
rpm_thread = threading.Thread(target=update_rpm, daemon=True)
rpm_thread.start()

# Start the sensor reading in a separate thread
sensor_thread = threading.Thread(target=read_sensors, daemon=True)
sensor_thread.start()

def RunStateMachine():
    global flag1, flag2, rpm, battV, coolV, coolF, last_update_time, flag_reverse

    current_time = time.time()

    match mainstate:
        case "init":
            thread1.welcome_screen_()
            return
        
        case "idle":
            if not flag2:
                thread1.creating_all_function_trigger()
                flag2 = True
                return
            
            if flag_reverse:
                # rpm_thread.start()
                thread1.hide_reverse_feed()
                flag_reverse = False
                return

        case "reverse":
            # rpm_thread.stop()
            thread1.show_reverse_feed()
            flag_reverse = True
        
        case "map":
            return
    if not flag_reverse:
        update_idle(current_time)


if __name__ == "__main__":
    t_init = time.time()

    while True:
        t = time.time()
        t_elapsed = t - t_init

    
        RunStateMachine()
        thread1.update()

        if t >= t_init + 4 and mainstate == "init":
            mainstate = "idle"

        # # If we are in "idle" state and we detect voltage on the reverse lights
        # # put it in reverse state
        if (mainstate == "idle") and (ina3.getBusVoltage_V() > 10):
            mainstate = "reverse"

        if (mainstate == "reverse") and (ina3.getBusVoltage_V() < 10):
            mainstate = "idle"
        
