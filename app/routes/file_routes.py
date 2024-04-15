# app/routes/file_routes.py

import os
import csv
import uuid
import xml.etree.ElementTree as ET
from flask import Blueprint, send_from_directory, request, jsonify
from app.db import MySQL


file_routes = Blueprint('file_routes', __name__)

@file_routes.route("/convert", methods=["POST"])
def convert():
    json_data = request.json
    
    if json_data is None:
        return "No JSON data received", 400
    
    xml_string = json_data.get('xml')
    
    if xml_string is None:
        return "No XML data found in JSON payload", 400

    try:
        # Parse XML string
        root = ET.fromstring(xml_string)

        # Extract data and write to CSV
        csv_data = []
        headers = set()
        for child in root:
            row = {}
            for elem in child:
                headers.add(elem.tag)
                row[elem.tag] = elem.text
            csv_data.append(row)

        if not os.path.exists('downloads'):
            os.makedirs('downloads')

        filename = f'res{uuid.uuid4()}.csv'
        csv_path = os.path.join('downloads', filename)

        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=sorted(list(headers)))
            writer.writeheader()
            for row in csv_data:
                writer.writerow(row)

        return filename
    except Exception as e:
        return f"Error processing XML data: {str(e)}", 500


@file_routes.route("/download/<filename>")
def download(filename):
    return send_from_directory('downloads', filename, download_name = 'result.csv')

@file_routes.route("/upload", methods=["POST"])
def upload():
    mysql = MySQL()
    json_data = request.json

    if json_data is None:
        return "No JSON data received", 400

    xml_string = json_data["xml"]
    filename = json_data["fileName"]
    content_type = json_data["contentType"]

    if not all([xml_string, filename, content_type]):
        return "Missing required fields in JSON data", 400

    # Save data to the database
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO XMLfiles (filename, contentType, xmlString, timestamp) VALUES (%s, %s, %s, CURRENT_TIMESTAMP)",
                (filename, content_type, xml_string))
    mysql.connection.commit()
    cur.close()

    return "File uploaded successfully!"

@file_routes.route("/files", methods=["GET"])
def get_files():
    mysql = MySQL()
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, filename, contentType, timestamp FROM XMLfiles")
    files = cur.fetchall()
    cur.close()

    # Prepare response
    response = []
    for file in files:
        file_data = {
            "id": file[0],
            "filename": file[1],
            "contentType": file[2],
            "timestamp": file[3].strftime("%Y-%m-%d %H:%M:%S") if file[3] else None
        }
        response.append(file_data)

    return jsonify(response)
