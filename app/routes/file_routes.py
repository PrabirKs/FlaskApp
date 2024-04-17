# app/routes/file_routes.py

# app/routes/file_routes.py

import os
import csv
import uuid
import xml.etree.ElementTree as ET
from flask import Blueprint, send_from_directory, request, jsonify
from app.dbSql import get_db
from app.service.fileConverter import tsv_to_xlsx,csv_to_xlsx,xml_to_xlsx,json_to_xlsx

file_routes = Blueprint('file_routes', __name__)

@file_routes.route("/convert", methods=["POST"])
def convert():
    json_data = request.json
    
    if json_data is None:
        return "No JSON data received", 400
    
    xml_string = json_data.get('content')
    
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

@file_routes.route("/convert2", methods=["POST"])
def convert2():
    json_data = request.json
    
    if json_data is None:
        return "No JSON data received", 400
    
    content_type = json_data['contentType']
    data = json_data['content']

    if content_type == 'text/xml':
        try:
            filename = xml_to_xlsx(data)
            return filename
        except Exception as e:
            return f"Error converting XML to XLSX: {str(e)}", 500
    
    elif content_type == 'text/csv':
        try:
            filename = csv_to_xlsx(data)
            return filename
        except Exception as e:
            return f"Error converting CSV to XLSX: {str(e)}", 500
    elif content_type == 'text/tsv':
        try:
            filename = tsv_to_xlsx(data)
            return filename
        except Exception as e:
            return f"Error converting CSV to XLSX: {str(e)}", 500

    elif content_type == 'application/json':
        try:
            filename = json_to_xlsx(data)
            return filename
        except Exception as e:
            return f"Error converting JSON to XLSX: {str(e)}", 500
    
    else:
        return "Unsupported content type", 400

@file_routes.route("/download/<filename>")
def download(filename):
    return send_from_directory('downloads', filename, download_name='result.csv')

@file_routes.route("/upload", methods=["POST"])
def upload():
    db = get_db()
    json_data = request.json

    if json_data is None:
        return "No JSON data received", 400

    xml_string = json_data.get("content")
    filename = json_data.get("fileName")
    content_type = json_data.get("contentType")

    if not all([xml_string, filename, content_type]):
        return "Missing required fields in JSON data", 400

    # Save data to the database
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO XMLfiles (filename, contentType, xmlString, timestamp) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
        (filename, content_type, xml_string),
    )
    db.commit()
    cursor.close()

    return "File uploaded successfully!"

@file_routes.route("/files", methods=["GET"])
def get_files():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT id, filename, contentType, timestamp FROM XMLfiles"
    )
    files = cursor.fetchall()
    cursor.close()

    # Prepare response
    response = []
    for file in files:
        file_data = {
            "id": file[0],
            "filename": file[1],
            "contentType": file[2],
            "timestamp": file[3].strftime("%Y-%m-%d %H:%M:%S") if file[3] else None,
        }
        response.append(file_data)

    return jsonify(response)
