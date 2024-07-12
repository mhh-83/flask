from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy


jwt = JWTManager()
app = Flask(__name__)


app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "supersecretkey"
app.config["UPLOAD_FOLDER"] = "static/files"


# mysql+ssh://pachim@185.79.98.202/pachim@127.0.0.1/data?name=lovely-nilofr&usePrivateKey=true
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://pachim:haghshenas67@localhost:3306/data'
db = SQLAlchemy(app)





