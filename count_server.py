from gpiozero import Button, LED
from datetime import datetime, timezone
from time import sleep
import pytz
import csv
import json
from flask import Flask, jsonify, send_file, redirect,url_for,render_template
import threading
import os
import logging 

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("counter_log")

def flash_led(times, on_time=0.5, off_time=0.5):
    """
    Function to flash an LED a given number of times.
    
    Parameters:
    times (int): Number of times to flash the LED
    on_time (float): Time in seconds the LED stays on during each flash
    off_time (float): Time in seconds the LED stays off during each flash
    """
    print("flashing")
    for _ in range(times):
        led.on()
        sleep(on_time)
        led.off()
        sleep(off_time)

# Set up the buttons on GPIO pins 19,20,and 26
m_button = Button(19,bounce_time = 0.1)  #press after medication
b_button = Button(20,bounce_time = 0.1)  #press getting in or out of bed
p_button = Button(26,bounce_time = 0.1)  #press after pee

# Set up the LED on GPIO pin 5
led = LED(5)

#signal the user that we're about ready to go
flash_led(5,.2,.2)


# CSV file path
csv_file_path = 'button_press_log.csv'

## Function to log date and time in Central time
def log_datetime(btn_id):
    
    logging.basicConfig(level=logging.DEBUG)
    logger.info("datetime " + btn_id)
     
     
    central = pytz.timezone('America/Chicago')
    # Get the current time in UTC
    now_utc = datetime.now(pytz.utc)
    
    # Get the timezone for Central Time
    central = pytz.timezone('America/Chicago')
    
    # Convert the current UTC time to Central Time
    now_central = now_utc.astimezone(central)
    logger.info("now central: " + now_central.strftime('%d %b %Y %H%M'))
    
    # Format the datetime object to the desired format
    day = now_central.strftime("%d-%m-%Y")
    hour = now_central.strftime("%H%M")
    data =[day,hour,btn_id]
    
    with open(csv_file_path, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(data)
        
    #signal the user that we have recorded the button press
    flash_led(3,.2,.2)

# Attach the functions to the button press events
p_button.when_pressed = lambda: log_datetime('P')
m_button.when_pressed = lambda: log_datetime('M')
b_button.when_pressed = lambda: log_datetime('B')

# ============== routes ===============

@app.route('/')
def index():
    return render_template("index.html")   
    


@app.route('/data', methods=['GET'])
def get_data():
    output = [] 
    try:
        with open(csv_file_path,'r') as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                if(row):  #ignore empty row
                    logger.info(row)
                    output.append({"timestamp": row})  #TODO; Fix format
            
    except FileNotFoundError:
        return jsonify({"error": "No data found"}), 404
    logger.info(jsonify(output))
    return jsonify(output)

# Route to download the raw CSV file
@app.route('/download', methods=['GET'])
def download_file():
    return send_file(csv_file_path, as_attachment=True)

# Route to delete the log file
@app.route('/delete', methods=['DELETE'])
def delete_data():
    try:
        os.remove(csv_file_path)
        return jsonify({"message": "Data deleted successfully"}), 200
    except FileNotFoundError:
        app.logger.warning('could not delete csv data')
        return jsonify({"error": "No data found to delete"}), 404


#Function to run Flask app in a separate thread
def run_server():
    app.run(host='0.0.0.0', port=5555, debug=False)

# Start the Flask server in a separate thread
threading.Thread(target=run_server).start()

# Keep the script running
print("Waiting for button press...")
p_button.wait_for_press()
m_button.wait_for_press()

