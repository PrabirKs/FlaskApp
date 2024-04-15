from flask import Flask,request,send_from_directory,jsonify
from flask_mysqldb import MySQL
import os
import pandas as pd
import uuid
from flask_cors import CORS
import csv
import xml.etree.ElementTree as ET

app = Flask(__name__)
CORS(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'TRADB'

# Create a MySQL connection object
mysql = MySQL(app)


@app.route("/")
def hello():
    return "hello"

@app.route("/test")
def index():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * from test')
    data = cur.fetchall()
    return str(data)

@app.route("/save", methods=['GET', 'POST'])
def handle_test():
    if request.method == 'POST':
        testId = request.json.get('testId')
        name = request.json.get('name')
        if testId is not None and name is not None:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO test (testId, name) VALUES (%s, %s)", (testId, name))
            mysql.connection.commit()
            cur.close()
            return "Data inserted successfully!"
        else:
            return "Missing testid or name in request body", 400
    elif request.method == 'GET':
        cur = mysql.connection.cursor()
        cur.execute('SELECT * from test')
        data = cur.fetchall()
        return str(data)

@app.route("/convert", methods=["POST"])
def convert():
    json_data = request.json  # Assuming JSON payload is sent in the request
    
    # Extract XML string from JSON payload
    xml_string = json_data['xml']
    
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

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory('downloads', filename, download_name = 'result.csv')

@app.route("/upload", methods=["POST"])
def upload():
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

@app.route("/files", methods=["GET"])
def get_files():
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

if __name__ == "__main__":
    app.run(debug=True)