# __init__.py

from flask import Flask
from app.config import Config
from flask_cors import CORS
from app.routes.test_routes import test_routes
from app.routes.file_routes import file_routes
from app.dbSql import init_db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    init_db(app)

    app.register_blueprint(test_routes)
    app.register_blueprint(file_routes)

    return app
