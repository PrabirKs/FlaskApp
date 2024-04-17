import os
import io
import csv
import json
import uuid
import xml.etree.ElementTree as ET
import pandas as pd
import xlsxwriter
from openpyxl import load_workbook
def xml_to_csv(xml_string):
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
    
def xml_to_xlsx(xml_string):
    try:
        root = ET.fromstring(xml_string)
        csv_data = []
        headers = set()
        for child in root:
            row = {}
            for elem in child:
                headers.add(elem.tag)
                row[elem.tag] = elem.text
            csv_data.append(row)

        df = pd.DataFrame(csv_data)
        filename = f'res{uuid.uuid4()}.xlsx'
        filepath = os.path.join('downloads', filename)
        df.to_excel(filepath, index=False)  # Removed print statement
        return filename
    except Exception as e:
        print(f"Error processing XML data: {str(e)}")  # Print the error message
        return f"Error processing XML data: {str(e)}", 500
def json_to_xlsx(json_string):
    try:
        data = json.loads(json_string)
        df = pd.DataFrame(data)
        df = df.fillna("")
        filename = f'res{uuid.uuid4()}.xlsx'
        filepath = os.path.join('downloads', filename)
        df.to_excel(filepath, index=False)
        return filename
    except Exception as e:
        print(f"Error processing JSON data: {str(e)}")
        return f"Error processing JSON data: {str(e)}", 500

def csv_to_xlsx(csv_string):
    try:
        df = pd.read_csv(io.StringIO(csv_string))
        filename = f'res{uuid.uuid4()}.xlsx'
        filepath = os.path.join('downloads', filename)
        df.to_excel(filepath, index=False)
        return filename
    except Exception as e:
        print(f"Error processing CSV data: {str(e)}")
        return f"Error processing CSV data: {str(e)}", 500

def tsv_to_xlsx(tsv_string):
    try:
        df = pd.read_csv(io.StringIO(tsv_string), sep='\t')
        filename = f'res{uuid.uuid4()}.xlsx'
        filepath = os.path.join('downloads', filename)
        df.to_excel(filepath, index=False)
        return filename
    except Exception as e:
        print(f"Error processing TSV data: {str(e)}")
        return f"Error processing TSV data: {str(e)}", 500
def xlsx_to_xlsx(xlsx_string):
    try:
        # Generate a unique filename
        filename = f'res{uuid.uuid4()}.xlsx'
        
        # Define the file path to save the XLSX file
        filepath = os.path.join('downloads', filename)
        
        # Save the XLSX string to the specified file path
        with open(filepath, 'wb') as file:
            file.write(xlsx_string.encode('utf-8'))
        
        return filename
    except Exception as e:
        return f"Error converting XLSX string to XLSX file: {str(e)}", 500