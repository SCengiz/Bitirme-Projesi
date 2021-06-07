import numpy as np
import my_lcd
import time, datetime
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
from pad4pi import rpi_gpio
import json
import hashlib
from pyfingerprint.pyfingerprint import PyFingerprint

# GPIO pins used for security check results.
led_17 = 17
led_22 = 22
buzzer = 27

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(led_17, GPIO.OUT)
GPIO.setup(led_22, GPIO.OUT)
GPIO.setup(buzzer, GPIO.OUT)

GPIO.output(led_17, GPIO.LOW)
GPIO.output(led_22, GPIO.LOW)
GPIO.output(buzzer, GPIO.LOW)

# Setup for Keypad
KEYPAD \
    = [ 
        ["1","2","3","A"],
        ["4","5","6","B"],
        ["7","8","9","C"],
        ["*","0","#","D"]
      ]

# 16x2 LCD interface
# ...display is an instance of my_lcd class.
display = my_lcd.lcd()
display.lcd_clear()
display.lcd_backlight(0)

# Rows and Cols for the Keypad
ROW_PINS = [6, 13, 19, 26] 
COL_PINS = [12, 16, 20, 21] 

# ...factory is a Keypad instance. 
# ...create() function is used for generate a setup.
factory = rpi_gpio.KeypadFactory()
keypad = factory.create_keypad(keypad=KEYPAD, row_pins=ROW_PINS, col_pins=COL_PINS)

# reader is a rf-id module instance.
reader = SimpleMFRC522()

# used variables for this work
# ...password_input is a global variable used for 4 digit password test.
# ...The pin is a 4 digit password variable that we set here.
pin = ['4', '5', '1', '2']
glob_password_input = []
glob_copy  = []
glob_extra = []  

# new_data function is a starting function.
def new_data():
    display.lcd_clear()
    display.lcd_display_string(" Starting !!! ", 1)
    time.sleep(1)
    
# clear function is used for clear the lcd display.
def clear():
    global glob_password_input
    global glob_extra
    global glob_copy
    glob_password_input, glob_extra, glob_copy  = [ [],[],[] ]    
    display.lcd_clear()
    display.lcd_display_string(" Password : ", 1)

# done function is basically copy the entered 4 digit password.
def done():
    global glob_copy
    glob_copy = glob_password_input

# info function is used when we entered wrong password.
# ...if we entered wrong password the setup gives us a second change for the enterance.
def info():
    display.lcd_clear()
    display.lcd_display_string('Wrong Password', 1)
    time.sleep(1)
    display.lcd_display_string('Try Again', 2)
    time.sleep(1)
    display.lcd_clear()

# Take_Password function is checking the validity for the entered 4 digit password.
def Take_Password(key):
    global glob_password_input
    global glob_extra
    if key == '*':
        clear()
    else:
        if len(glob_password_input) != 4:
            glob_extra.append('*')
            glob_password_input.append(key)
            display.lcd_display_string(glob_extra, 2)
        else:
            if key=='#':
                if glob_password_input == pin:
                    GPIO.output(led_17, GPIO.HIGH)
                    done()
                    time.sleep(2)
                    GPIO.output(led_17, GPIO.LOW)
        
                else:
                    GPIO.output(led_22, GPIO.HIGH)
                    info()
                    clear()
                    GPIO.output(led_22, GPIO.LOW)
                    
            else:
                pass

# rf_test function is used for card detection and check the permission.
def rf_test():
    display.lcd_display_string("Hold the card : ", 1)
    id, member = reader.read()
    
    member = member.strip()
        
    if id:
        display.lcd_clear()
        display.lcd_display_string("Detected", 1)
        time.sleep(1)
        
        display.lcd_clear() 
        display.lcd_display_string("Member: ", 1)
        display.lcd_display_string(member, 2)
        time.sleep(1)
               
        display.lcd_clear()
        display.lcd_display_string("RF-ID Card: ", 1)
        display.lcd_display_string(str(id), 2)
        time.sleep(1)
        
        display.lcd_clear()          

        read_date  = datetime.datetime.now()
        right_date = read_date.strftime("%d/%m/%Y")
        display.lcd_display_string(right_date ,1)
        
        right_time = read_date.strftime("%H:%M:%S")
        display.lcd_display_string(right_time, 2)

        time.sleep(1)
        display.lcd_clear() 
            
        tuple_data = (member, id, right_date, right_time)
        
        for item in tuple_data:
            print(item)
            
        return tuple_data

# check function is checking the permission of fingerprint and rf-id card.
def check():
    tuple_data   = rf_test()
    tuple_data_member = tuple_data[1]
    
    saved_ids_in_file = []
    with open("rf_saved_id.txt") as file_op:
        saved_ids_in_file = file_op.readlines()
    
    datas = saved_ids_in_file
    perm = ""
        
    flag = 0
    for item in datas:
        if int(item) == tuple_data_member:
            flag = 1

# try-except block for fingerprint sensor.
    try:
        f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

        if ( f.verifyPassword() == False ):
            raise ValueError('The given fingerprint sensor password is wrong!')

    except Exception as e:
        print('The fingerprint sensor could not be initialized!')
        print('Exception message: ' + str(e))
        exit(1)

    if flag == 1:    
        display.lcd_clear()
        display.lcd_display_string('Correct', 1)
        GPIO.output(led_17, True)
        time.sleep(1)
        GPIO.output(led_17, False)
        try:
            print('Waiting for finger...')
            display.lcd_clear()
            display.lcd_display_string('Waiting for ', 1)
            display.lcd_display_string('  Finger', 2)
            time.sleep(1)
            
            ## Wait that finger is read
            while ( f.readImage() == False ):
                pass

            ## Converts read image to characteristics and stores it in charbuffer 1
            f.convertImage(0x01)

            ## Searchs template
            result = f.searchTemplate()

            positionNumber = result[0]
            accuracyScore = result[1]
            if ( positionNumber == -1 ):
                display.lcd_clear()
                display.lcd_display_string('not Correct', 1)
                GPIO.output(buzzer, True)
                time.sleep(1)
                GPIO.output(buzzer, False)
                perm = "NP"
            
            else:
                display.lcd_clear()
                display.lcd_display_string('Correct', 1)
                GPIO.output(led_17, True)
                time.sleep(1)
                GPIO.output(led_17, False)
                perm = "P"                
#                print('Found template at position #' + str(positionNumber))
#                print('The accuracy score is: ' + str(accuracyScore))

        except Exception as e:
            print('Operation failed!')
            print('Exception message: ' + str(e))
            print('No match found!')
            display.lcd_clear()
            display.lcd_display_string('not Correct', 1)
            GPIO.output(buzzer, True)
            time.sleep(1)
            GPIO.output(buzzer, False)
            perm = "NP"

    else:
        display.lcd_clear()
        display.lcd_display_string('not Correct', 1)
        print("not Correct")
        GPIO.output(buzzer, True)
        time.sleep(1)
        GPIO.output(buzzer, False)
        perm = "NP"
        
    take_datas = {}
        
    name       = tuple_data[0]
    rf_number  = tuple_data[1]
    date_now   = tuple_data[2]
    time_now   = tuple_data[3]
    permission = perm 
    
    take_datas[name] = {'RF-ID' : rf_number , 'DATE' : date_now, 'TIME' : time_now, 'PERMISSON' : permission}
        
    with open('J_new.json', 'a') as ff:
        json.dump(take_datas, ff)

    
display.lcd_display_string(" Password : ", 1)
keypad.registerKeyPressHandler(Take_Password)

try:
    new_data()
    while(True):
        
        if glob_copy == pin:
            display.lcd_clear()
            display.lcd_display_string('TRUE',1)
            time.sleep(1)
            check()
            display.lcd_clear()
            display.lcd_display_string('Next Member', 1)
            time.sleep(1)
            clear()
            new_data()
            
    time.sleep(0.2)
    
except KeyboardInterrupt:
    GPIO.cleanup()
    display.lcd_clear()
    keypad.cleanup()


