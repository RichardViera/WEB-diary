from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import date

class Diaries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(150))
    entry = db.Column(db.String(2500))
    date = db.Column(db.Date)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150), unique=True)
    status = db.Column(db.Integer)
    diary = db.relationship('Diaries')