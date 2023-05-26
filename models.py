from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import datetime

db = SQLAlchemy()

#from .models import User
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))
    sex = db.Column(db.String(6))
    natid = db.Column(db.String(20), unique=True)
    address = db.Column(db.String(100))
    phone = db.Column(db.String(10))
    img = db.Column(db.String(100))
    role = db.Column(db.Integer)

    def __init__(self, fname, lname, sex, natid, address, phone, img, role):
        self.fname=fname
        self.lname=lname
        self.sex=sex
        self.natid=natid
        self.address=address
        self.phone=phone
        self.img=img
        self.role=role


class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100))
    title = db.Column(db.String(100))
    sex = db.Column(db.String(6))
    part = db.Column(db.String(100))
    image = db.Column(db.String(100))

    def __init__(self, fullname, title, sex, part, image):
        self.fullname=fullname
        self.title=title
        self.sex=sex
        self.part=part
        self.image=image

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidateid = db.Column(db.Integer)
    userid = db.Column(db.Integer)

    def __init__(self, candidateid, userid):
        self.candidateid=candidateid
        self.userid=userid


class Publish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Integer)
    period = db.Column(db.Integer)

    def __init__(self, status, period):
        self.status=status
        self.period=period
