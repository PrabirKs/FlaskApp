import os
import csv
import json
import uuid
import xml.etree.ElementTree as ET
import pandas as pd

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
        test = df.to_excel(filepath, index=False)
        print(test)
        return filename
    except Exception as e:
        raise e

def csv_to_xlsx(csv_string):
    try:
        # Assuming csv_string is the content of a CSV file
        df = pd.read_csv(pd.compat.StringIO(csv_string))
        filename = f'res{uuid.uuid4()}.xlsx'
        filepath = os.path.join('downloads', filename)
        df.to_excel(filepath, index=False)
        return filename
    except Exception as e:
        raise e

def json_to_xlsx(json_string):
    print("start")
    try:
        data = json.loads(json_string)
        df = pd.DataFrame(data)
        filename = f'res{uuid.uuid4()}.xlsx'
        filepath = os.path.join('downloads', filename)
        df.to_excel(filepath, index=False)
        return filename
    except Exception as e:
        raise e
