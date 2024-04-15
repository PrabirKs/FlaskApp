# app/routes/test_routes.py

from flask import Blueprint, jsonify, request
from app.db import MySQL

test_routes = Blueprint('test_routes', __name__)

@test_routes.route("/test")
def index():
    mysql = MySQL()
    cur = mysql.connection.cursor()
    cur.execute('SELECT * from XmlFIles')
    data = cur.fetchall()
    cur.close()
    return jsonify(data)
