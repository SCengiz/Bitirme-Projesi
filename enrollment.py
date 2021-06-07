import RPi.GPIO as GPIO
import time
from mfrc522 import SimpleMFRC522
from pyfingerprint.pyfingerprint import PyFingerprint

GPIO.setwarnings(False)

reader = SimpleMFRC522()

try:
    new_member = input('New Member Name and Surname:')
    print("Please place the card")
# write() function detect the card and save it with its name and surname.
    reader.write(new_member)
    print("Saved new member : ", new_member)
# read() function is reading the cards id number.
    id, new_member = reader.read()
    print("Card ID          : ", id)
    
# id saving to the file with our created "rf_saved_id.txt" 
    file_saved_ids = open("rf_saved_id.txt", "a")
    file_saved_ids.write(str(id) + " " + "\n")
    file_saved_ids.close()

finally:
    GPIO.cleanup()

# A try-except block for the activation of FingerPrint sensor
# ...f is a class instance of the PyFingerprint
# ...We use an USB-TTL convertor in USB0 port
# ...57600 is a boudrate for the fingerprint sensor.
try:
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

    if ( f.verifyPassword() == False ):
        raise ValueError('The given fingerprint sensor password is wrong!')

except Exception as e:
    print('The fingerprint sensor could not be initialized!')
    print('Exception message: ' + str(e))
    exit(1)

print('Currently used fingerprint templates: '\
      + str(f.getTemplateCount()) +'/'+ str(f.getStorageCapacity()))

try:
    print('Waiting for finger...')

# Wait that finger is read
    while ( f.readImage() == False ):
        pass

# Converts read image to characteristics and stores it in charbuffer 1
    f.convertImage(0x01)

# Checks if finger is already enrolled
    result = f.searchTemplate()
    positionNumber = result[0]

    if ( positionNumber >= 0 ):
        print('Template already exists at position #' + str(positionNumber))
        exit(0)

    print('Remove finger...')
    time.sleep(2)

    print('Waiting for same finger again...')

# Wait that finger is read again
    while ( f.readImage() == False ):
        pass

# Converts read image to characteristics and stores it in charbuffer 2
    f.convertImage(0x02)

# Compares the charbuffers
    if ( f.compareCharacteristics() == 0 ):
        raise Exception('Fingers do not match')

# Creates a template
    f.createTemplate()

# Saves template at new position number
    positionNumber = f.storeTemplate()
    print('Finger enrolled successfully!')
    print('New template position #' + str(positionNumber))

except Exception as e:
    print('Operation failed!')
    print('Exception message: ' + str(e))
    exit(1)

