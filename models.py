from werkzeug.security import generate_password_hash, check_password_hash
from confige import db
from sqlalchemy import String, Column, String, Integer, Text
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, PasswordField
from wtforms.validators import InputRequired, EqualTo, Length


from datetime import datetime

class UploadForm(FlaskForm):
    file = FileField("Files", [InputRequired()] )
    submit = SubmitField("Upload")
    
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(Integer, primary_key=True)
    username = db.Column(String(20), nullable=False, unique=True)
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
                    if data[key] is int:
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
    id = db.Column(Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)
    part = db.Column(db.String(20), nullable=False)
    level = db.Column(db.Integer(), nullable=False)
    data = db.Column(db.JSON(), nullable=False)
    @classmethod
    def get_data(cls, type, part, level):
        return cls.query.filter_by(type=type, part=part, level=level).first()
    @classmethod
    def max_levels(cls, type, part):
        return len(cls.query.filter_by(type=type, part=part).all())
class TokenBlocklist(db.Model):
    id = db.Column(Integer, primary_key=True)
    jti = db.Column(db.String(10), nullable=True)
    create_at = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return f"<Token {self.jti}>"
    
    def save(self):
        db.session.add(self)
        db.session.commit()
class UserInterface(db.Model):
    __tablename__ = "game_data"
    id = db.Column(Integer, primary_key=True)
    data = db.Column(db.JSON())
class ResetPassWord(FlaskForm):
    password = PasswordField('New Password', [InputRequired(), EqualTo('confirm', message='گذرواژگان باید یکی باشند'), Length(8, 20, message="حداقل طول گذرواژه 8 و حداکثر آن 20 حرف می باشد")])
    confirm  = PasswordField('Repeat Password', [InputRequired()])
    submit = SubmitField("تغییر")
    token = ""
    def set_data(self, password, confirm):
        self.password.default = password
        self.confirm.default = confirm

class Book(db.Model):
    id = Column("id", Integer, primary_key=True)
    link = Column("link", String(200), nullable=False)
    img_refrence = Column("img_refrence", String(200), nullable=False)
    name = Column("name", String(50), nullable=False)
    writer = Column("writer", String(40), nullable=False)
    description = Column("description", Text())
    