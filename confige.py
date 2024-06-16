from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

jwt = JWTManager()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://pachim:haghshenas67@185.79.98.202/data"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "supersecretkey"
app.config["UPLOAD_FOLDER"] = "static/files"
db = SQLAlchemy(app)
