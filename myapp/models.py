from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from enum import Enum
db = SQLAlchemy()




class IDCardEnum(Enum):
    visitor = 'visitor'
    permanent = 'permanent'
    not_applicable = 'not_applicable'


class ApprovalStatusEnum(Enum):
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'




class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_fname = db.Column(db.String(100), nullable=False)
    user_lname = db.Column(db.String(100), nullable=False)
    user_phone = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(100), nullable=False, unique=True)
    user_pwd = db.Column(db.String(200))

    def set_password(self, password):
        self.user_pwd = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.user_pwd, password)
    

class Admin(db.Model):
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_username = db.Column(db.String(100),nullable=False)
    admin_password = db.Column(db.String(200),nullable=False)
    admin_loggedin = db.Column(db.DateTime, default=datetime.utcnow)



class UserRequest(db.Model):
    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fullname = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    job_role = db.Column(db.String(200), nullable=False)
    email_address = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(100), nullable=False)
    id_card = db.Column(db.Enum(IDCardEnum), default=IDCardEnum.visitor)
    expected_date = db.Column(db.Date)
    departure_date = db.Column(db.Date)
    duration = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    purpose =  db.Column(db.String(250), nullable=False)
    status = db.Column(db.Enum(ApprovalStatusEnum), default=ApprovalStatusEnum.PENDING)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    user = db.relationship('User', backref='requests')
    document = db.Column(db.String(255))








  