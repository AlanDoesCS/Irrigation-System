import time
import os
import signal
import sys
import Adafruit_ADS1x15

# ADS1115 configuration
I2C_ADDRESS = 0x48
I2C_BUSNUM = 1
GAIN = 2/3
CHANNEL = 0

# Moisture thresholds (in %)
MOISTURE_LOW_THRESHOLD  = 30.0   # Below this, pump ON
MOISTURE_HIGH_THRESHOLD = 70.0   # Above this, pump OFF

# Initialize ADC and pump state
adc = Adafruit_ADS1x15.ADS1115(address=I2C_ADDRESS, busnum=I2C_BUSNUM)
pump_on = False

def handle_exit(signum, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

print("Starting moisture monitoring loop. Press Ctrl+C to exit.")
try:
    while True:
        raw_value = adc.read_adc(CHANNEL, gain=GAIN)
        moisture_percent = round(max(0.0, min(100.0, (raw_value / 32767.0) * 100.0)), 1)
        print(f"Moisture: {moisture_percent}%  (ADC raw = {raw_value})")

        if moisture_percent >= MOISTURE_HIGH_THRESHOLD and pump_on:
            os.system("echo '1-1' > /sys/bus/usb/drivers/usb/unbind")
            pump_on = False
            print("** Moisture above threshold: turning pump OFF **")
        elif moisture_percent <= MOISTURE_LOW_THRESHOLD and not pump_on:
            os.system("echo '1-1' > /sys/bus/usb/drivers/usb/bind")
            pump_on = True
            print("** Moisture below threshold: turning pump ON **")
            
        time.sleep(1.0)
except KeyboardInterrupt:
    print("\nExiting moisture monitoring.")
    sys.exit(0)
