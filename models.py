from collections.abc import Sequence
from typing import Any, Mapping
from confige import db
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import InputRequired
from flask_login import UserMixin
import bcrypt

class UploadForm(FlaskForm):
    file = FileField("Files", [InputRequired()] )
    
    submit = SubmitField("Upload")
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100), unique=False, nullable=False)
    score = 0
    def __init__(self, username, password):
       self.username = username
       self.password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    def check_password(self, password):
        return bcrypt.checkpw(password.encode("utf-8"), self.password.encode("utf-8"))

    def to_json(self, filter=[]):
        data = {}
        if filter != []:
            for t in filter:
                data[t] = self.get(t)
        else:
            data = {
            "username":self.username,
            "password":self.password
        }
        return data