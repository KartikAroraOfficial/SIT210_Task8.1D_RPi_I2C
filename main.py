from signal import signal, SIGTERM, SIGHUP, pause
from time import sleep
from threading import Thread
import smbus as BUS
from rpi_lcd import LCD

bus = BUS.SMBus(2)      	# declared after making custom I2C pins from terminal using command: "sudo dtoverlay i2c-gpio bus=2 i2c_gpio_sda=22 i2c_gpio_scl=23" 

reading = True
message = ""

lcd = LCD()					# uses 0x27 by default

def safe_exit(signum, frame):
    exit(1)

def display_intensity():
    global message
    while reading:
        print(message)
        lcd.text(message, 1)
        sleep(0.25)

def measure_intensity():
    global message

    while reading:
        data = bus.read_i2c_block_data(0x23,0x23)
        sensor_value = ((data[1] + (256*data[0]))/1.2)
        if (sensor_value < 30):
            message = "Too Dark"
        elif (sensor_value < 50):
            message = "Dark"
        elif (sensor_value < 200):
            message = "Medium"
        elif (sensor_value < 350):
            message = "Bright"
        else:
            message = "Too Bright"
            
        sleep(0.1)

try:
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)

    reader = Thread(target=measure_intensity, daemon=True)
    display = Thread(target=display_intensity, daemon=True)

    reader.start()
    display.start()

    pause()

except KeyboardInterrupt:
    pass

finally:
    reading = False
    reader.join()
    display.join()
    lcd.clear()