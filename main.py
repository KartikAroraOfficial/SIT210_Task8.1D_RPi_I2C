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

def display_intensity():    # displays the intensity of light as measured by the measure_intensity functions on both the LCD and the console 
    global message
    while reading:
        print(message)
        lcd.text(message, 1)

        sleep(0.25)

def measure_intensity():    # measures the intensity of light and decides whether it's Dark, Too Dark, Bright, Too Bright or Medium.
    global message

    while reading:
        
        # reads the data from the I2C system manager bus 
        data = bus.read_i2c_block_data(0x23,0x23)
        sensor_value = ((data[1] + (256*data[0]))/1.2)

        # categorizing the intensity by value 
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


# main body of the program 
try:

    # exiting safely on receiving terminate/ hang up signal
    signal(SIGTERM, safe_exit)
    signal(SIGHUP, safe_exit)

    # 2 threads to run our functions in the background.
    reader = Thread(target=measure_intensity, daemon=True)
    display = Thread(target=display_intensity, daemon=True)

    # starting the threads
    reader.start()
    display.start()

    # pauses the program to wait for the signals
    pause()     

except KeyboardInterrupt:
    pass

finally:
    # turning the global variable running false
    reading = False
    
    # Ending the background process
    reader.join()
    display.join()

    # clearing the LCD screen
    lcd.clear()