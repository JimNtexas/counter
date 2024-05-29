from gpiozero import Button
from datetime import datetime, timezone
import pytz
import csv
import json
from flask import Flask, jsonify, send_file
import threading
import os
import logging 

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# Set up the buttonS on GPIO pinS 26 and 19
p_button = Button(26,bounce_time = 0.1)  #press after pee
m_button = Button(19,bounce_time = 0.1)  #press after medication


# CSV file path
csv_file_path = 'button_press_log.csv'

# Function to log date and time in Central time
def log_datetime(btn_id):
    
    app.logger.info("logging button " + btn_id)
    app.logger.setLevel(logging.WARNING)
     
    central = pytz.timezone('America/Chicago')
    # Get the current time in UTC
    now_utc = datetime.now(pytz.utc)
    
    # Get the timezone for Central Time
    central = pytz.timezone('America/Chicago')
    
    # Convert the current UTC time to Central Time
    now_central = now_utc.astimezone(central)
    
    # Format the datetime object to the desired format
    formatted_now_central = now_central.strftime("%d-%m-%Y - %H%M " + btn_id)
    
    print("debug - " + str(formatted_now_central))
    
    with open(csv_file_path, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([str(formatted_now_central)])
        print(f'Button pressed at {formatted_now_central}')

# Attach the functions to the button press events
p_button.when_pressed = log_datetime('P')
m_button.when_pressed = log_datetime('M')

# Route to download the data in JSON format
@app.route('/data', methods=['GET'])
def get_data():
    data = []
    try:
        with open(csv_file_path, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                if row:  # Skip empty rows
                    data.append({"timestamp": row[0]})
    except FileNotFoundError:
        return jsonify({"error": "No data found"}), 404
    return jsonify(data)

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

# Function to run Flask app in a separate thread
def run_server():
    app.run(host='10.211.1.98', port=5555, debug=False)

# Start the Flask server in a separate thread
threading.Thread(target=run_server).start()

# Keep the script running
print("Waiting for button press...")
p_button.wait_for_press()
m_button.wait_for_press()
