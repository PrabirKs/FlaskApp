# app/routes/process_routes.py

import threading
import time
import os
import csv
import xml.etree.ElementTree as ET
from flask import Blueprint, request, jsonify, Response
from app.db import MySQL
import uuid
process_routes = Blueprint('process_routes', __name__)

@process_routes.route("/process", methods=["POST"])
def process():
    # Get the XML data from the request
    xml_data = request.data
    
    # Start a separate thread to perform processing asynchronously
    thread = threading.Thread(target=perform_processing, args=(xml_data,))
    thread.start()

    # Return a response indicating the processing has started
    return Response("Processing started", status=200)

def perform_processing(xml_data):
    # Task 1: Save XML file to the database
    save_to_database(xml_data)
    
    # Task 2: Convert XML to CSV
    convert_to_csv(xml_data)
    
    # Task 3: Clean the data
    clean_data()
    
    # Task 4: Send a download link
    send_download_link()

def save_to_database(xml_data):
    # Save data to the database
    # This function should be implemented based on your database model and requirements
    pass

def convert_to_csv(xml_data):
   time.sleep(2)
   return "data converted to csv"

def clean_data():
    # Clean the data
    # This function should be implemented based on your data cleaning requirements
    time.sleep(2)
    return "data cleaned"

def send_download_link():
    # Send the download link
    # This function should be implemented based on how you want to provide the download link to the user
    time.sleep(2)
    return "link send"

def send_progress_updates():
    while True:
        # Send progress updates to the frontend every 2 seconds
        status = "progress"  # Assuming the task is still in progress
        # You can determine the status based on the progress of each task
        
        # Send the status to the frontend
        send_progress(status)
        
        # Wait for 2 seconds before sending the next update
        time.sleep(2)

def send_progress(status):
    response = jsonify({"status": status})
    response.status_code = 200
    response.headers["Content-Type"] = "application/json"
    return response

# Start a separate thread to send progress updates
progress_thread = threading.Thread(target=send_progress_updates)
progress_thread.start()
