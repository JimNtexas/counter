print ("Counter0"
       )

# button_logger.py
from gpiozero import Button
from datetime import datetime, timezone
import csv

# Set up the button on GPIO pin 4
button =button = Button(4)

# Function to log date and time in GMT
def log_datetime():
    now = datetime.now(timezone.utc)
    with open('button_press_log.csv', 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([now.isoformat()])
    print(f'Button pressed at {now.isoformat()}')

# Attach the function to the button press event
button.when_pressed = log_datetime

# Keep the script running
print("Waiting for button press...")
button.wait_for_press()
