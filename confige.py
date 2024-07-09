from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from sshtunnel import SSHTunnelForwarder

jwt = JWTManager()
app = Flask(__name__)



forwarding_server = SSHTunnelForwarder(
    ('185.79.98.202', 22),
    ssh_username="pachim",
    ssh_password="haghshenas67",
    remote_bind_address=('127.0.0.1', 3306)
)
forwarding_server.start()
local_port = forwarding_server.local_bind_port
# mysql+ssh://pachim@185.79.98.202/pachim@127.0.0.1/data?name=lovely-nilofr&usePrivateKey=true
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://pachim:haghshenas67@127.0.0.1:{}/data'.format(local_port)
db = SQLAlchemy(app)



app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "supersecretkey"
app.config["UPLOAD_FOLDER"] = "static/files"



