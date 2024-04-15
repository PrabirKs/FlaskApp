# app/routes/test_routes.py

# app/routes/test_routes.py

from flask import Blueprint, jsonify
from app.dbSql import get_db

test_routes = Blueprint('test_routes', __name__)

@test_routes.route("/test")
def index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM test')
    data = cursor.fetchall()
    print(data)
    cursor.close()
    return "test index"

