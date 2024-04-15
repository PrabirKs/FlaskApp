from app import create_app
import os
import sys


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)