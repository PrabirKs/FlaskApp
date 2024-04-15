# import pyodbc

# conn = pyodbc.connect('DRIVER={SQL Server};SERVER=SW0103021\\SQLEXPRESS;DATABASE=prabir;UID=Prabira;PWD=12345')

# cursor = conn.cursor()
# cursor.execute("select * from test")
# row = cursor.fetchall()

# for i in row:
#     print(i)

# db.py

import pyodbc
from flask import g, current_app

def get_db():
    if 'db' not in g:
        # Connect to SQL Server database
        g.db = pyodbc.connect(
            'DRIVER={SQL Server};SERVER=SW0103021\\SQLEXPRESS;DATABASE=prabir;UID=Prabira;PWD=12345'
        )
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    app.teardown_appcontext(close_db)
