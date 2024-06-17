from werkzeug.security import generate_password_hash, check_password_hash
from confige import db
from sqlalchemy import String, Column
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import InputRequired
from uuid import uuid4
from datetime import datetime

class UploadForm(FlaskForm):
    file = FileField("Files", [InputRequired()] )
    submit = SubmitField("Upload")
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(), primary_key=True, default=str(uuid4()))
    username = db.Column(db.String(), nullable=False, unique=True)
    phone = Column(String(11), nullable=False, default="09", unique=True)
    password = db.Column(db.Text(), nullable=False)
    data = db.Column(db.JSON())
    
    def update(self, data, overwrite):
        if overwrite:
            for key in self.data.keys():
                if not data.get(key):
                    data[key]=self.data.get(key)
            return data
        else:
            d = {}
            for key in self.data.keys():
                if not data.get(key):
                    data[key]=self.data.get(key)
                else:
                    data[key] += self.data.get(key)
                    d[key] = data[key]
            return [data, d]
    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @classmethod
    def get_user_by_username(cls, username):
        return cls.query.filter_by(username=username).first()
    @classmethod
    def get_user_by_phone(cls, phone):
        return cls.query.filter_by(phone=phone).first()
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Levels(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    type = db.Column(db.String(), nullable=False)
    part = db.Column(db.String(), nullable=False)
    level = db.Column(db.Integer(), nullable=False)
    data = db.Column(db.JSON(), nullable=False)
    @classmethod
    def get_data(cls, type, part, level):
        return cls.query.filter_by(type=type, part=part, level=level).first()
    @classmethod
    def max_levels(cls, type, part):
        return len(cls.query.filter_by(type=type, part=part).all())
class TokenBlocklist(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    jti = db.Column(db.String(), nullable=True)
    create_at = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return f"<Token {self.jti}>"
    
    def save(self):
        db.session.add(self)
        db.session.commit()
class UserInterface(db.Model):
    __tablename__ = "game_data"
    id = db.Column(db.String(), primary_key=True, default=str(uuid4()))
    data = db.Column(db.JSON())